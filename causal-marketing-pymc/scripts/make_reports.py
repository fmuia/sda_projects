"""Generate a clean PDF report per notebook: narrative + plots + printed results,
with code inputs and sampler-progress noise stripped out."""
import sys, re, copy, subprocess, os
from pathlib import Path
import nbformat
from nbconvert import PDFExporter
from traitlets.config import Config

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "reports"; OUT.mkdir(exist_ok=True)

# Glyphs xelatex's default fonts silently drop (esp. inside code spans / verbatim
# output). We map them to LaTeX-safe text so the report never loses characters.
# Real $...$ math blocks use LaTeX commands (\tau, \mu, ...) and are unaffected.
GLYPHS = {
    # decorative star in the two anchor titles ("… ⭐ ANCHOR A"); the word ANCHOR
    # is already in the text, so drop the glyph rather than inject a second "ANCHOR".
    "⭐": "", "\U0001f7e1": "(yellow) ", "\U0001f534": "(red) ",
    "\U0001f7e2": "(green) ", "⚪": "(white) ",
    # greek (as used in code spans / prose / printed output)
    "τ": "tau", "β": "beta", "μ": "mu", "α": "alpha", "γ": "gamma", "σ": "sigma",
    "δ": "delta", "ρ": "rho", "λ": "lambda", "κ": "kappa", "π": "pi", "ε": "eps",
    "θ": "theta", "η": "eta", "ν": "nu", "ω": "omega", "χ": "chi",
    "Δ": "Delta", "Σ": "Sigma", "μ̂": "mu_hat", "τ̂": "tau_hat", "β̂": "beta_hat",
    "̂": "",  # stray combining circumflex
    # operators / relations
    "≈": "~", "≥": ">=", "≤": "<=", "≠": "!=", "×": "x", "→": "->", "←": "<-",
    "⇒": "=>", "√": "sqrt", "∑": "sum", "∈": " in ", "∏": "prod", "∂": "d",
    "∞": "inf", "≫": ">>", "≪": "<<", "±": "+/-",
    # sub/superscripts
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5", "₆": "6",
    "⁰": "0", "¹": "1", "²": "^2", "³": "^3",
    # marks
    "✓": "[ok]", "✗": "[x]", "⚠": "[!]",
}
# Sampler-progress noise to strip from stdout/stderr. Each alternative is anchored on a
# FULL PyMC/BART message prefix (with `.match`, i.e. line-start), NOT a bare token: an
# earlier version keyed on generic words (`Only`, `Chain`, `Computing`, `>`, `took`,
# `tree depth`, `jitter`) that also matched legitimate result lines — e.g. "Only 3 of 30
# markets cleared the bar", "took €5 per customer", "> a note", "Chain retailers saw…" —
# and silently deleted them from the PDF (a fail-open leak of real content). The optional
# leading `>*` catches PyMC's nested sub-sampler lines (">NUTS: […]", ">>PGBART: […]").
# Verified against all 48 sampler lines in the committed notebooks (all still stripped)
# and 11 look-alike result lines (none stripped).
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


_KEYS = sorted(GLYPHS, key=len, reverse=True)   # multi-codepoint keys (τ̂) before single (τ)


def sanitize(text):
    for k in _KEYS:
        text = text.replace(k, GLYPHS[k])
    return text


def first_title(nb):
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            for ln in cell.source.splitlines():
                if ln.startswith("# "):
                    return sanitize(ln[2:].strip())
    return "Report"


def clean(nb):
    nb = copy.deepcopy(nb)
    nb.metadata["title"] = first_title(nb)
    nb.metadata.pop("authors", None)
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            cell.source = sanitize(cell.source)
        if cell.cell_type == "code":
            outs = []
            for o in cell.get("outputs", []):
                if o.get("output_type") == "stream" and o.get("name") == "stderr":
                    continue
                if o.get("output_type") == "stream":
                    lines = [ln for ln in o["text"].splitlines() if not NOISE.match(ln.strip())]
                    if not "".join(lines).strip():
                        continue
                    o["text"] = sanitize("\n".join(lines) + "\n")
                # sanitize text in execute_result / display_data plain-text reprs too
                if o.get("output_type") in ("execute_result", "display_data"):
                    data = o.get("data", {})
                    if "text/plain" in data:
                        data["text/plain"] = sanitize(data["text/plain"])
                outs.append(o)
            cell.outputs = outs
    return nb


def main():
    names = sorted(REPO.glob("notebooks/*.ipynb"))
    # Staleness guard: a notebook with un-executed code cells would render a stale
    # or blank-output PDF that ships silently. Warn loudly (per notebook) so a
    # "regenerate reports without re-running" mistake is visible, not invisible.
    stale = []
    for nb_path in names:
        nbk = nbformat.read(nb_path, as_version=4)
        unrun = sum(1 for c in nbk.cells if c.cell_type == "code"
                    and "".join(c.get("source", "")).strip()
                    and c.get("execution_count") is None)
        if unrun:
            stale.append((nb_path.stem, unrun))
    if stale:
        print("WARNING — notebooks with UN-EXECUTED code cells (their PDF will be stale):")
        for n, k in stale:
            print(f"  - {n}: {k} un-run code cell(s); re-execute before shipping the report")
    c = Config()
    c.PDFExporter.exclude_input = True          # hide code, keep outputs (narrative report)
    c.PDFExporter.exclude_input_prompt = True
    c.PDFExporter.exclude_output_prompt = True
    c.PDFExporter.latex_count = 1
    exporter = PDFExporter(config=c)
    ok, fail = [], []
    for nb_path in names:
        nb = clean(nbformat.read(nb_path, as_version=4))
        try:
            body, _ = exporter.from_notebook_node(nb)
            (OUT / (nb_path.stem + ".pdf")).write_bytes(body)
            ok.append(nb_path.stem)
            print("OK  ", nb_path.stem)
        except Exception as e:
            fail.append((nb_path.stem, str(e)[:300]))
            print("FAIL", nb_path.stem, "-", str(e)[:200])
    print(f"\n{len(ok)} ok, {len(fail)} fail")
    for n, e in fail: print(" -", n, e[:150])


if __name__ == "__main__":
    main()
