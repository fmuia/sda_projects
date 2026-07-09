# causal-marketing-pymc — common tasks
# Two environments (see README "Environment split"):
#   .venv         core, pymc>=6  (notebooks 00-05, 07; all marimo apps)
#   .venv-legacy  legacy, pymc<6 (notebooks 06, 08-11; causalpy + pymc-marketing)

CORE   = .venv/bin
LEGACY = .venv-legacy/bin

.PHONY: help env env-legacy kernels apps app-uplift app-confounding app-sc test test-fast test-legacy reports clean

help:
	@echo "make env          - create/refresh the core env (pymc>=6) with uv"
	@echo "make env-legacy   - create/refresh the legacy env (pymc<6) for causalpy/pymc-marketing"
	@echo "make kernels      - register both venvs as Jupyter kernels (cmp-core, cmp-legacy)"
	@echo "make apps         - list the interactive marimo apps and how to serve them"
	@echo "make app-uplift / app-confounding / app-sc  - serve one marimo app"
	@echo "make test         - execute every notebook headless in FAST mode + run pytest"
	@echo "make test-fast    - pytest smoke tests on the shared package only"
	@echo "make test-legacy  - truth-recovery tests for the CausalPy DiD/ITS/IV estimators (legacy env)"

env:
	uv sync --python 3.12

env-legacy:
	uv venv .venv-legacy --python 3.12
	uv pip install --python $(LEGACY)/python -r requirements-legacy.txt
	uv pip install --python $(LEGACY)/python -e . --no-deps

kernels:
	$(CORE)/python -m ipykernel install --user --name cmp-core --display-name "Python (cmp core, pymc6)"
	$(LEGACY)/python -m ipykernel install --user --name cmp-legacy --display-name "Python (cmp legacy, pymc5)"

apps:
	@echo "Interactive marimo apps (reactive; also open as plain notebooks with 'marimo edit'):"
	@echo "  make app-uplift        # uplift policy explorer"
	@echo "  make app-confounding   # confounding sensitivity"
	@echo "  make app-sc            # synthetic-control placebo"
	@echo "Deploy to in-browser WASM for the lecture:  marimo export html-wasm apps/<file>.py -o site/"

app-uplift:
	$(CORE)/marimo run apps/uplift_policy_explorer.py

app-confounding:
	$(CORE)/marimo run apps/confounding_sensitivity.py

app-sc:
	$(CORE)/marimo run apps/synthetic_control_placebo.py

test:
	$(CORE)/python -m pytest tests/ -v

test-fast:
	$(CORE)/python -m pytest tests/test_package.py -v

test-legacy:  ## truth-recovery guards for the CausalPy DiD/ITS/IV estimators (legacy env)
	CMP_FAST=1 $(LEGACY)/python -m pytest tests/test_estimators_legacy.py -v

reports:  ## render one PDF per notebook (narrative + plots) into reports/ ; needs xelatex on PATH
	PATH="/Library/TeX/texbin:$$PATH" $(CORE)/python scripts/make_reports.py

clean:
	rm -rf .pytest_cache **/__pycache__ notebooks/*.html site/
