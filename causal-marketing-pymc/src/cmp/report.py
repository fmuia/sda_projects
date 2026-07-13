"""Export notebook results to the book — so no number is ever retyped.

The book (`book/`) is generated from the *executed* notebooks. Rounds 2 and 3 of this
repo's history were largely about prose that had drifted from the output it described
(a "€15.3k" that the FULL run printed as 15.2; an "ESS in the hundreds" that was 3268;
a decision-flipping "33 markets" against a printed 27). Hand-copying results into a
second narrative would turn that accident into a system.

So the notebooks *emit* their results, and the book *injects* them:

    cmp.report.value("nb07.sc_total", 318_400, unit="EUR")   -> \\nbSevenScTotal
    cmp.report.table(df,  "nb07.compare", caption="...")     -> build/tables/nb07_compare.tex
    cmp.report.figure(fig,"nb07.sc",      caption="...")     -> build/figures/nb07_sc.pdf

`make book` then writes `build/macros.tex` and compiles. Two properties we want:

* a stale number is impossible — the macro resolves to whatever the notebook last printed;
* a *missing* number is a LaTeX compile error, not a silent blank. That is a feature: the
  book refuses to build rather than ship a hole.

Figures are re-rendered in **book style** (larger type, no in-figure title — the caption
does that job, vector PDF), because a figure sized for a notebook cell is not a figure
sized for a printed page.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent.parent
BUILD = REPO / "book" / "build"
RESULTS = BUILD / "results.json"

__all__ = ["value", "table", "figure", "load", "book_style", "macro_name"]

# ---------------------------------------------------------------- naming
_WORD = {"0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four", "5": "Five",
         "6": "Six", "7": "Seven", "8": "Eight", "9": "Nine", "b": "b"}


def macro_name(key: str) -> str:
    r"""'nb07.sc_total' -> '\nbSevenScTotal'. LaTeX macro names may only contain letters,
    so digits become words ('07' -> 'Seven', '07b' -> 'SevenB', '11b' -> 'ElevenB')."""
    nb, _, rest = key.partition(".")
    m = re.fullmatch(r"nb(\d+)(b?)", nb)
    if not m:
        raise ValueError(f"key must start with nbNN[b]. — got {key!r}")
    num, suffix = m.group(1), m.group(2)
    words = {"00": "Zero", "01": "One", "02": "Two", "03": "Three", "04": "Four",
             "05": "Five", "06": "Six", "07": "Seven", "08": "Eight", "09": "Nine",
             "10": "Ten", "11": "Eleven"}
    if num not in words:
        raise ValueError(f"unknown notebook number {num!r}")
    head = "nb" + words[num] + ("B" if suffix else "")
    tail = "".join(p.capitalize() for p in re.split(r"[_\W]+", rest) if p)
    name = head + tail
    if not name.isalpha():
        # A LaTeX macro name may contain letters ONLY. A key like "nb10.cl_r2" would produce
        # \nbTenClR2, which TeX parses as \nbTenClR followed by the digit 2 — so the build fails
        # with "Undefined control sequence \nbTenClR", pointing nowhere near the key that caused
        # it, and it fails for the WHOLE book. Catch it here, at the emit site, where the fix is
        # obvious: spell the digit out ("cl_r_two", "cl_rsq").
        raise ValueError(
            f"key {key!r} makes the macro \\{name}, which is not a legal LaTeX macro name "
            f"(letters only — digits are not allowed). Spell the digits out: e.g. 'cl_r2' -> "
            f"'cl_rsq' or 'cl_r_two'."
        )
    return "\\" + name


SHARDS = BUILD / "results"


def _nb_of(key: str) -> str:
    """'nb07b.sc_total' -> 'nb07b'. The shard a key belongs to."""
    return key.partition(".")[0]


def _shard_path(nb: str) -> Path:
    return SHARDS / f"{nb}.json"


def _store(nb: str) -> dict:
    """Read ONE notebook's shard.

    Results are sharded per notebook rather than kept in a single results.json because the
    chapters are built by many notebooks running concurrently, and a shared file would be a
    read-modify-write race: two notebooks emitting at once would each write back a dict missing
    the other's keys. The book would then fail to compile — or worse, compile with a chapter's
    numbers silently gone. A notebook only ever writes its own shard, so there is nothing to race
    on. `load()` merges the shards at build time.
    """
    p = _shard_path(nb)
    return json.loads(p.read_text()) if p.exists() else {}


def _write(nb: str, store: dict) -> None:
    SHARDS.mkdir(parents=True, exist_ok=True)
    # Write-then-rename: a reader (or a concurrent `make book`) never observes a half-written file.
    tmp = _shard_path(nb).with_suffix(".json.tmp")
    tmp.write_text(json.dumps(store, indent=2, sort_keys=True))
    tmp.replace(_shard_path(nb))


def _latex_escape(s: str) -> str:
    """pandas' own escaping, reproduced so `math_headers` can invert it on the header row."""
    for a, b in (("\\", r"\textbackslash "), ("_", r"\_"), ("^", r"\textasciicircum "),
                 ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde ")):
        s = s.replace(a, b)
    return s


def _check_kind(store: dict, key: str, kind: str | None) -> None:
    """One key, one kind. A `figure("nb07.decision")` landing on top of a
    `value("nb07.decision")` would silently delete the macro the chapter cites — and the book
    would then fail to compile for a reason ("undefined \\nbSevenDecision") that points nowhere
    near the cause. Re-emitting the SAME kind is fine and expected (a notebook is re-run); it is
    a change of kind that is always a naming mistake."""
    prev = store.get(key)
    if prev is None:
        return
    prev_kind = prev.get("kind")            # None == scalar
    if prev_kind != kind:
        raise ValueError(
            f"key {key!r} is already registered as a {prev_kind or 'value'} and cannot be "
            f"re-emitted as a {kind or 'value'}. Rename one of them — a key names exactly one "
            f"result."
        )


# ---------------------------------------------------------------- emit
def value(key: str, val, *, unit: str = "", fmt: str | None = None, note: str = ""):
    """Record a scalar the book will typeset. Returns `val` so it can wrap an expression:

        att = report.value("nb08.att", att_cluster.estimate, unit="EUR", fmt=",.0f")

    `fmt` is a Python format spec applied at emit time (the book prints the string as-is,
    so rounding is decided here, once, next to the computation that produced it).
    """
    macro_name(key)                                    # validate early, fail loudly
    if isinstance(val, (np.floating, np.integer)):
        val = val.item()
    text = format(val, fmt) if (fmt and isinstance(val, (int, float))) else str(val)
    nb = _nb_of(key)
    store = _store(nb)
    _check_kind(store, key, None)
    store[key] = {"value": val, "text": text, "unit": unit, "note": note}
    _write(nb, store)
    return val


def table(df, key: str, *, caption: str, label: str | None = None, fmt: str = "%.2f",
          align: str | None = None, note: str = "", math_headers: bool = False):
    """Write a pandas DataFrame as a booktabs LaTeX table the chapter can \\input.

    `math_headers=True` passes the column headers through to LaTeX unescaped, so a header may
    carry math (`$\\varphi$`, `$\\hat\\tau$`). The default escapes everything, which is right for
    the *cells* — a euro sign or a per-cent in a data cell must not be read as LaTeX — but it also
    mangles a header that was written as math into the literal text `\\$\\textbackslash varphi\\$`.
    Escaping cells and typesetting headers are different jobs; this flag separates them.
    """
    macro_name(key)
    BUILD.joinpath("tables").mkdir(parents=True, exist_ok=True)
    path = BUILD / "tables" / (key.replace(".", "_") + ".tex")
    body = df.to_latex(index=False, escape=True, float_format=lambda v: fmt % v,
                       column_format=align or ("l" + "r" * (df.shape[1] - 1)),
                       caption=caption, label=label or f"tab:{key.replace('.', ':')}",
                       position="htbp")
    if math_headers:
        # Put the ORIGINAL header text back, unescaped. Only the header row is affected: the
        # cells stay escaped, because a "€" or a "%" in a data cell is data, not LaTeX.
        esc = " & ".join(_latex_escape(str(c)) for c in df.columns) + r" \\"
        raw = " & ".join(str(c) for c in df.columns) + r" \\"
        if esc in body:
            body = body.replace(esc, raw, 1)
        else:                                          # pandas changed its escaping — fail loudly
            raise RuntimeError(
                f"table({key!r}, math_headers=True): could not locate the escaped header row to "
                f"restore. Escaping the headers would silently mangle the math, so this refuses "
                f"rather than shipping a broken table."
            )
    # to_latex emits \toprule/\midrule/\bottomrule with booktabs=True by default in
    # modern pandas; be explicit so the chapter's preamble requirement is unambiguous.
    #
    # Book typography, applied once here rather than argued about per table: results tables are
    # centred and set one step down from the body text, with tighter column gutters. A results
    # table with seven columns does not fit an A4 text block at body size, and a table that
    # overruns the margin is a defect the chapter cannot fix from its side.
    body = body.replace(r"\begin{tabular}",
                        "\\centering\n\\small\n\\setlength{\\tabcolsep}{4.5pt}\n\\begin{tabular}",
                        1)
    nb = _nb_of(key)
    store = _store(nb)
    _check_kind(store, key, "table")
    path.write_text(body)
    store[key] = {"kind": "table", "path": str(path.relative_to(REPO)), "caption": caption,
                  "note": note}
    _write(nb, store)
    return path


def figure(fig, key: str, *, caption: str, label: str | None = None, width: str = r"\linewidth",
           note: str = ""):
    """Save a matplotlib figure as a vector PDF for the book, in book style.

    The notebook keeps its own inline rendering; this writes a SECOND copy sized and styled
    for a printed page. In-figure titles are stripped: in a book the caption carries the
    takeaway, and a title above a caption is redundant.
    """
    macro_name(key)
    BUILD.joinpath("figures").mkdir(parents=True, exist_ok=True)
    path = BUILD / "figures" / (key.replace(".", "_") + ".pdf")
    for ax in fig.get_axes():
        ax.set_title("")                                # the caption does this work
    nb = _nb_of(key)
    store = _store(nb)
    _check_kind(store, key, "figure")
    fig.savefig(path, format="pdf", bbox_inches="tight", metadata={"Creator": "cmp.report"})
    store[key] = {"kind": "figure", "path": str(path.relative_to(REPO)), "caption": caption,
                  "label": label or f"fig:{key.replace('.', ':')}", "width": width,
                  "note": note}
    _write(nb, store)
    return path


# ---------------------------------------------------------------- consume
def load() -> dict:
    """Merge every notebook's shard into one dict. This is what the book builds from."""
    merged: dict = {}
    if SHARDS.exists():
        for p in sorted(SHARDS.glob("*.json")):
            merged.update(json.loads(p.read_text()))
    if RESULTS.exists():                                  # legacy single-file store
        merged.update(json.loads(RESULTS.read_text()))
    return merged


def write_macros(path: Path | None = None) -> Path:
    """Generate build/macros.tex: one \\newcommand per emitted scalar."""
    store = load()
    path = path or (BUILD / "macros.tex")
    lines = ["% Generated by cmp.report — do not edit. Every number here came from an",
             "% executed notebook. If a macro is missing, the book will not compile:",
             "% that is deliberate (a hole is louder than a stale number).", ""]
    for key, rec in sorted(store.items()):
        if rec.get("kind") in ("table", "figure"):
            continue
        lines.append(rf"\newcommand{{{macro_name(key)}}}{{{rec['text']}}}")
    path.write_text("\n".join(lines) + "\n")
    return path


def book_style():
    """Matplotlib rcParams for figures destined for the printed page (call inside the
    notebook only when emitting; the notebook's own inline style is unchanged)."""
    return {
        "figure.dpi": 150, "savefig.dpi": 300,
        "font.size": 11, "axes.titlesize": 11, "axes.labelsize": 11,
        "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "legend.fontsize": 9.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "pdf.fonttype": 42,                              # embed real fonts, not Type-3
    }
