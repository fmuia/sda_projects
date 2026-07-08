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
    "⭐": "[ANCHOR] ", "\U0001f7e1": "(yellow) ", "\U0001f534": "(red) ",
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
NOISE = re.compile(r"(Sampling|Multiprocess|Sequential|Only|We recommend|The rhat|The effective|"
                   r"There were|Chain|Auto-assigning|CompoundStep|PGBART|NUTS|Initializing|"
                   r"Computing|The acceptance|>|jitter|took|tree depth|Sampling:)")


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
