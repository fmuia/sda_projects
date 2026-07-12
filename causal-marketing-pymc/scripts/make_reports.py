"""Generate a clean PDF report per notebook: narrative + plots + printed results,
with code inputs and sampler-progress noise stripped out.

Unicode policy (two different worlds, two different rules):

* **Prose (markdown cells)** is typeset by LaTeX, so real Unicode is *kept* and
  rendered properly: a preamble of `\\newunicodechar` mappings turns each glyph into
  the correct LaTeX construct (→ becomes \\rightarrow, ≈ becomes \\approx, τ becomes
  \\tau, …). Transliterating these to ASCII ("->", ">=", "tau") is what a code comment
  looks like, not a lecture note — it is not acceptable in the report.
* **Printed output (code cells)** lands inside a verbatim environment, where LaTeX
  macros do not run and the monospace font is what it is. There we *do* fall back to
  ASCII (VERBATIM_GLYPHS) so nothing silently vanishes into a missing-glyph box.

Because prose keeps its Unicode, every glyph the notebooks actually use must have a
mapping — `check_glyph_coverage()` fails loudly if a new one shows up unmapped, so a
missing character can never silently ship as a blank box.
"""
import copy
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import nbformat
from nbconvert import LatexExporter
from traitlets.config import Config

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "reports"; OUT.mkdir(exist_ok=True)
XELATEX = shutil.which("xelatex") or "/Library/TeX/texbin/xelatex"

# --------------------------------------------------------------------------------------
# 1. Prose: real Unicode, typeset via \newunicodechar. Keys are the characters as they
#    appear in the notebooks (see check_glyph_coverage). Multi-codepoint combos (τ̂) are
#    handled by PROSE_COMBOS below, which runs first.
# --------------------------------------------------------------------------------------
# xcolor and amssymb are already loaded by nbconvert's LaTeX template (ANSI colours /
# math symbols), so \textcolor and \checkmark are available; \providecommand guards the
# latter in case a future template drops amssymb.
UNICODE_MATH = {
    # relations / operators
    "≈": r"\ensuremath{\approx}", "≠": r"\ensuremath{\neq}",
    "≤": r"\ensuremath{\leq}",    "≥": r"\ensuremath{\geq}",
    "≫": r"\ensuremath{\gg}",     "≪": r"\ensuremath{\ll}",
    "×": r"\ensuremath{\times}",  "÷": r"\ensuremath{\div}",
    "±": r"\ensuremath{\pm}",     "∓": r"\ensuremath{\mp}",
    "−": r"\ensuremath{-}",       "·": r"\ensuremath{\cdot}",
    "√": r"\ensuremath{\surd}",   "⊥": r"\ensuremath{\perp}",
    "∑": r"\ensuremath{\sum}",    "∏": r"\ensuremath{\prod}",
    "∈": r"\ensuremath{\in}",     "∂": r"\ensuremath{\partial}",
    "∞": r"\ensuremath{\infty}",  "∫": r"\ensuremath{\int}",
    # arrows
    "→": r"\ensuremath{\rightarrow}", "←": r"\ensuremath{\leftarrow}",
    "⇒": r"\ensuremath{\Rightarrow}", "⇐": r"\ensuremath{\Leftarrow}",
    "↑": r"\ensuremath{\uparrow}",    "↓": r"\ensuremath{\downarrow}",
    # greek
    "α": r"\ensuremath{\alpha}", "β": r"\ensuremath{\beta}",  "γ": r"\ensuremath{\gamma}",
    "δ": r"\ensuremath{\delta}", "ε": r"\ensuremath{\epsilon}", "ζ": r"\ensuremath{\zeta}",
    "η": r"\ensuremath{\eta}",   "θ": r"\ensuremath{\theta}", "κ": r"\ensuremath{\kappa}",
    "λ": r"\ensuremath{\lambda}", "μ": r"\ensuremath{\mu}",   "ν": r"\ensuremath{\nu}",
    "π": r"\ensuremath{\pi}",    "ρ": r"\ensuremath{\rho}",   "σ": r"\ensuremath{\sigma}",
    "τ": r"\ensuremath{\tau}",   "φ": r"\ensuremath{\varphi}", "χ": r"\ensuremath{\chi}",
    "ψ": r"\ensuremath{\psi}",   "ω": r"\ensuremath{\omega}",
    "Δ": r"\ensuremath{\Delta}", "Σ": r"\ensuremath{\Sigma}", "Ω": r"\ensuremath{\Omega}",
    # sub/superscripts
    "⁰": r"\ensuremath{^0}", "¹": r"\ensuremath{^1}", "²": r"\ensuremath{^2}",
    "³": r"\ensuremath{^3}",
    "₀": r"\ensuremath{_0}", "₁": r"\ensuremath{_1}", "₂": r"\ensuremath{_2}",
    "₃": r"\ensuremath{_3}", "₄": r"\ensuremath{_4}", "₅": r"\ensuremath{_5}",
    "₆": r"\ensuremath{_6}",
    # marks / decoration
    "✓": r"\checkmark", "✗": r"\ensuremath{\times}", "⚠": r"\textbf{!}",
    "⭐": r"{}",  # decorative star in two anchor titles; the "(Anchor A)" label already says it
    # traffic-light legend: real coloured bullets beat "(yellow) "
    "\U0001f7e1": r"\textcolor{orange}{\ensuremath{\bullet}}",
    "\U0001f534": r"\textcolor{red}{\ensuremath{\bullet}}",
    "\U0001f7e2": r"\textcolor{green}{\ensuremath{\bullet}}",
    "⚪": r"\ensuremath{\circ}",
}
# Two-codepoint sequences (letter + COMBINING CIRCUMFLEX) must be rewritten before the
# single-char map sees the bare letter, or we would emit \tau followed by a stray accent.
PROSE_COMBOS = {
    "τ̂": r"\ensuremath{\hat{\tau}}", "μ̂": r"\ensuremath{\hat{\mu}}",
    "β̂": r"\ensuremath{\hat{\beta}}", "σ̂": r"\ensuremath{\hat{\sigma}}",
    "Δ̄": r"\ensuremath{\bar{\Delta}}",
}
# Glyphs the default font already sets correctly — left alone, no mapping needed.
PROSE_OK = set("—–…“”‘’€§°' ")


def latex_preamble():
    lines = [
        r"\usepackage{newunicodechar}",
        r"\providecommand{\checkmark}{\ensuremath{\surd}}",
        # The notebooks number their own sections ("6 · Decide, in euros"), and clean()
        # drops the H1 (the title comes from \maketitle) — so every H2 lands as a
        # \subsection under a phantom section 0 and LaTeX prefixes it "0.5". Turn the
        # automatic numbering off and let the authored headings speak for themselves.
        r"\setcounter{secnumdepth}{0}",
    ]
    for ch, cmd in UNICODE_MATH.items():
        lines.append(rf"\newunicodechar{{{ch}}}{{{cmd}}}")
    return "\n".join(lines)


def check_glyph_coverage(nbs):
    """Fail loudly if a notebook's prose uses a glyph we have no mapping for — otherwise
    xelatex would drop it into a silent blank box (the exact failure this file guards)."""
    unmapped = {}
    for path, nb in nbs:
        for cell in nb.cells:
            if cell.cell_type != "markdown":
                continue
            src = cell.source
            for combo in PROSE_COMBOS:
                src = src.replace(combo, "")
            for ch in src:
                if ord(ch) < 128 or ch in UNICODE_MATH or ch in PROSE_OK:
                    continue
                unmapped.setdefault(ch, set()).add(path.stem)
    if unmapped:
        print("ERROR — markdown uses glyphs with no LaTeX mapping (they would render as")
        print("        blank boxes). Add them to UNICODE_MATH in scripts/make_reports.py:")
        for ch, where in unmapped.items():
            print(f"  {ch!r}  U+{ord(ch):04X}  used in: {', '.join(sorted(where))}")
        sys.exit(1)


def prose(text):
    """Markdown: keep the Unicode (the preamble typesets it); only fold the combos."""
    for combo, cmd in PROSE_COMBOS.items():
        text = text.replace(combo, cmd)
    return text


# --------------------------------------------------------------------------------------
# 2. Printed output: verbatim, so LaTeX macros cannot run — ASCII fallbacks.
# --------------------------------------------------------------------------------------
VERBATIM_GLYPHS = {
    "⭐": "", "\U0001f7e1": "(amber) ", "\U0001f534": "(red) ",
    "\U0001f7e2": "(green) ", "⚪": "(white) ",
    "τ": "tau", "β": "beta", "μ": "mu", "α": "alpha", "γ": "gamma", "σ": "sigma",
    "δ": "delta", "ρ": "rho", "λ": "lambda", "κ": "kappa", "π": "pi", "ε": "eps",
    "θ": "theta", "η": "eta", "ν": "nu", "ω": "omega", "χ": "chi",
    "Δ": "Delta", "Σ": "Sigma", "μ̂": "mu_hat", "τ̂": "tau_hat", "β̂": "beta_hat",
    "̂": "",
    "≈": "~", "≥": ">=", "≤": "<=", "≠": "!=", "×": "x", "→": "->", "←": "<-",
    "⇒": "=>", "√": "sqrt", "∑": "sum", "∈": " in ", "∏": "prod", "∂": "d",
    "∞": "inf", "≫": ">>", "≪": "<<", "±": "+/-", "÷": "/", "·": "*", "−": "-",
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5", "₆": "6",
    "⁰": "0", "¹": "1", "²": "^2", "³": "^3",
    "✓": "[ok]", "✗": "[x]", "⚠": "[!]", "⊥": "_||_", "⟂": "_||_",
    "“": '"', "”": '"', "‘": "'", "’": "'",
}
_VKEYS = sorted(VERBATIM_GLYPHS, key=len, reverse=True)  # multi-codepoint (τ̂) before bare τ


def verbatim(text):
    for k in _VKEYS:
        text = text.replace(k, VERBATIM_GLYPHS[k])
    return text


# Sampler-progress noise to strip from stdout/stderr. Each alternative is anchored on a
# FULL PyMC/BART message prefix (with `.match`, i.e. line-start), NOT a bare token: an
# earlier version keyed on generic words (`Only`, `Chain`, `Computing`, `>`, `took`,
# `tree depth`, `jitter`) that also matched legitimate result lines — e.g. "Only 3 of 30
# markets cleared the bar", "took €5 per customer", "> a note", "Chain retailers saw…" —
# and silently deleted them from the PDF (a fail-open leak of real content). The optional
# leading `>*` catches PyMC's nested sub-sampler lines (">NUTS: […]", ">>PGBART: […]").
NOISE = re.compile(
    r">*\s*("
    r"Sampling \d|Sampling: \[|"
    r"Multiprocess sampling|Sequential sampling|"
    r"Auto-assigning NUTS|Initializing NUTS|"
    r"NUTS: \[|PGBART: \[|CompoundStep|BinaryGibbsMetropolis|Metropolis|Slice: \[|"
    r"Only \d+ samples per chain|"
    r"We recommend running at least|"
    r"The rhat statistic is|The effective sample size|The acceptance probability|"
    r"The number of (effective )?samples|"
    r"There (were|was) \d+ divergence|"
    r"Chain \d+ reached the maximum|Chain \d+ failed"
    r")")


def first_title(nb):
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            for ln in cell.source.splitlines():
                if ln.startswith("# "):
                    return prose(ln[2:].strip())
    return "Report"


def clean(nb):
    nb = copy.deepcopy(nb)
    nb.metadata["title"] = first_title(nb)
    nb.metadata.pop("authors", None)
    # The template renders metadata["title"] via \maketitle, so the notebook's own H1
    # would print the title twice on page 1 — drop the first H1 line only.
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            lines = cell.source.splitlines()
            for i, ln in enumerate(lines):
                if ln.startswith("# "):
                    cell.source = "\n".join(lines[:i] + lines[i + 1:]).lstrip("\n")
                    break
            break
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            cell.source = prose(cell.source)
        if cell.cell_type == "code":
            outs = []
            for o in cell.get("outputs", []):
                if o.get("output_type") == "stream" and o.get("name") == "stderr":
                    continue
                if o.get("output_type") == "stream":
                    lines = [ln for ln in o["text"].splitlines() if not NOISE.match(ln.strip())]
                    if not "".join(lines).strip():
                        continue
                    o["text"] = verbatim("\n".join(lines) + "\n")
                if o.get("output_type") in ("execute_result", "display_data"):
                    data = o.get("data", {})
                    # ipywidgets progress containers render as a literal "Output()" line.
                    data.pop("application/vnd.jupyter.widget-view+json", None)
                    if data.get("text/plain", "").strip() in ("Output()", "HBox()", "VBox()"):
                        continue
                    if not data:
                        continue
                    if "text/plain" in data:
                        data["text/plain"] = verbatim(data["text/plain"])
                outs.append(o)
            cell.outputs = outs
    return nb


def build_pdf(nb, exporter):
    """LaTeX -> inject the Unicode preamble -> xelatex (twice). We drive xelatex directly
    (rather than PDFExporter) so the preamble can be injected; a stale global
    ~/.jupyter/jupyter_nbconvert_config.json also makes `jupyter nbconvert --execute`
    unusable here, so keeping our own compile path avoids that trap entirely."""
    body, resources = exporter.from_notebook_node(nb)
    marker = r"\begin{document}"
    if marker not in body:
        raise RuntimeError("no \\begin{document} in exported LaTeX")
    body = body.replace(marker, latex_preamble() + "\n\n" + marker, 1)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "notebook.tex").write_text(body, encoding="utf-8")
        for name, data in (resources.get("outputs") or {}).items():
            (td / name).write_bytes(data)
        for _ in range(2):  # second pass settles refs/labels
            r = subprocess.run(
                [XELATEX, "-interaction=nonstopmode", "-halt-on-error", "notebook.tex"],
                cwd=td, capture_output=True, text=True)
        pdf = td / "notebook.pdf"
        if not pdf.exists():
            log = (td / "notebook.log").read_text(errors="replace") if (td / "notebook.log").exists() else r.stdout
            err = "\n".join(l for l in log.splitlines() if l.startswith("!"))[:400]
            raise RuntimeError(f"xelatex produced no PDF:\n{err}")
        return pdf.read_bytes()


def main():
    names = sorted(REPO.glob("notebooks/*.ipynb"))
    nbs = [(p, nbformat.read(p, as_version=4)) for p in names]

    # Staleness guard: a notebook with un-executed code cells would render a stale
    # or blank-output PDF that ships silently. Warn loudly (per notebook).
    stale = [(p.stem, k) for p, nb in nbs
             if (k := sum(1 for c in nb.cells if c.cell_type == "code"
                          and "".join(c.get("source", "")).strip()
                          and c.get("execution_count") is None))]
    if stale:
        print("WARNING — notebooks with UN-EXECUTED code cells (their PDF will be stale):")
        for n, k in stale:
            print(f"  - {n}: {k} un-run code cell(s); re-execute before shipping the report")

    check_glyph_coverage(nbs)  # exits non-zero on an unmapped glyph

    c = Config()
    c.LatexExporter.exclude_input = True          # hide code, keep outputs (narrative report)
    c.LatexExporter.exclude_input_prompt = True
    c.LatexExporter.exclude_output_prompt = True
    exporter = LatexExporter(config=c)

    ok, fail = [], []
    for path, nb in nbs:
        try:
            (OUT / (path.stem + ".pdf")).write_bytes(build_pdf(clean(nb), exporter))
            ok.append(path.stem)
            print("OK  ", path.stem)
        except Exception as e:
            fail.append((path.stem, str(e)[:300]))
            print("FAIL", path.stem, "-", str(e)[:200])
    print(f"\n{len(ok)} ok, {len(fail)} fail")
    for n, e in fail:
        print(" -", n, e[:150])
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
