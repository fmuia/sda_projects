# causal-marketing-pymc — common tasks
# Two environments (see README "Environment split"):
#   .venv         core, pymc>=6  (notebooks 00-05, 07, 07b; all marimo apps)
#   .venv-legacy  legacy, pymc<6 (notebooks 06, 08-11, 11b; causalpy + pymc-marketing)

CORE   = .venv/bin
LEGACY = .venv-legacy/bin

.PHONY: help env env-legacy kernels apps app-uplift app-confounding app-sc test test-fast test-legacy reports book clean

help:
	@echo "make env          - create/refresh the core env (pymc>=6) with uv"
	@echo "make env-legacy   - create/refresh the legacy env (pymc<6) for causalpy/pymc-marketing"
	@echo "make kernels      - register both venvs as Jupyter kernels (cmp-core, cmp-legacy)"
	@echo "make apps         - list the interactive marimo apps and how to serve them"
	@echo "make app-uplift / app-confounding / app-sc  - serve one marimo app"
	@echo "make test         - execute every notebook headless in FAST mode + run pytest"
	@echo "make test-fast    - pytest smoke tests on the shared package only"
	@echo "make test-legacy  - truth-recovery tests for the CausalPy DiD/ITS/IV estimators (legacy env)"
	@echo "make reports      - one lecture-handout PDF per notebook (reports/)"
	@echo "make book         - the book + chapter offprints (book/build/), numbers injected from the notebooks"

env:
	uv sync --python 3.12

env-legacy:
	uv venv .venv-legacy --python 3.12
	# install from the LOCK (exact pins incl. pygraphviz for pymc-marketing[dag]),
	# not the range file, so this matches CI and the committed nb06/08-11 outputs.
	uv pip install --python $(LEGACY)/python -r requirements-legacy.lock
	uv pip install --python $(LEGACY)/python -e . --no-deps

kernels:
	$(CORE)/python -m ipykernel install --user --name cmp-core --display-name "Python (cmp core, pymc6)"
	$(LEGACY)/python -m ipykernel install --user --name cmp-legacy --display-name "Python (cmp legacy, pymc5)"

apps:
	@echo "Interactive marimo apps (reactive; also open as plain notebooks with 'marimo edit'):"
	@echo "  make app-design        # experiment design: power / MDE / peeking   [WASM-safe]"
	@echo "  make app-uplift        # uplift policy explorer"
	@echo "  make app-confounding   # confounding sensitivity"
	@echo "  make app-sc            # synthetic-control placebo"
	@echo ""
	@echo "Ship to students as in-browser pages (no Python install):  make site"
	@echo "  WASM-safe = imports only Pyodide packages (numpy/scipy/statsmodels/sklearn/"
	@echo "  pandas/matplotlib). pymc, pytensor, arviz and the local 'cmp' package CANNOT"
	@echo "  load in the browser — a WASM app must be self-contained and precompute any"
	@echo "  posterior it needs, shipping the draws as data."

app-design:
	$(CORE)/marimo run apps/experiment_design.py

app-uplift:
	$(CORE)/marimo run apps/uplift_policy_explorer.py

app-confounding:
	$(CORE)/marimo run apps/confounding_sensitivity.py

app-sc:
	$(CORE)/marimo run apps/synthetic_control_placebo.py

app-iv:  ## Chapter 13 lecture (IV): foldable sections; loads the precomputed posterior draws
	$(CORE)/marimo run apps/iv_lecture.py

edit-iv:  ## same lecture in presenter/notebook mode (shows code, lets you tweak live)
	$(CORE)/marimo edit apps/iv_lecture.py

data-iv:  ## rebuild the IV lecture's data bundle (draws + nb11/nb11b scalars) and re-embed it
	# Run AFTER re-executing notebooks/11 (which writes the draws) so the euro figures and the
	# real-data section cite the notebooks' numbers, and the WASM export stays self-contained.
	$(CORE)/python apps/build_iv_lecture_data.py

html-iv:  ## build the standalone Quarto-style HTML lecture (apps/iv_lecture.html) — one offline file
	# Pre-renders every slider state to a PNG frame and inlines everything, so the single .html
	# opens in any browser with no server/runtime yet stays interactive. Reads the data-iv bundle.
	$(CORE)/python apps/build_iv_html.py

html-iv-slides:  ## build the Ch.13 interactive slide deck (apps/iv_slides.html) from iv_slides_src.html
	# Token-substitutes {{nb11.*}}/{{nb11b.*}} from the shards, bakes the draws + DGP params into
	# /*__DATA__*/, inlines MathJax. Edit apps/iv_slides_src.html, then rebuild.
	$(CORE)/python apps/build_iv_slides.py

html-iv-slides-sh:  ## build the management-first rework of the Ch.13 deck (apps/iv_slides_sh.html)
	# Same pipeline as html-iv-slides, different template/output. Edit apps/iv_slides_sh_src.html.
	$(CORE)/python apps/build_iv_slides_sh.py

html-geo:  ## build the standalone Ch.9 slide deck (apps/geo_lift_slides.html) — one offline file
	# Assembles apps/geo_slides_src.html: shard-token substitution (numbers never retyped),
	# the nb07 lecture bundle for the live charts, book figures inlined as PNGs, MathJax vendored.
	$(CORE)/python apps/build_geo_slides.py

html-labs:  ## build the business-applications closer deck (apps/labs_slides.html) — one offline file
	# Token-substitutes {{labs.*}} from apps/labs_deck_data.json (blog-pinned numbers carrying
	# source URLs — this deck's "shards"; no notebook results needed), injects the chart bundle,
	# inlines MathJax, then verifies every claim. Edit apps/labs_slides_src.html, then rebuild.
	$(CORE)/python apps/build_labs_slides.py
	$(CORE)/python apps/verify_labs_deck.py

html-geo-sh:  ## build the SHORT Ch.9 deck (apps/geo_lift_sh.html) — classical arc only, math folded
	# Same pipeline, from apps/geo_slides_sh_src.html: Title -> "Measure it, don't guess it"
	# (frequentist recommendation), business-concept-first with the algebra in fold-outs.
	$(CORE)/python apps/build_geo_slides.py --src apps/geo_slides_sh_src.html --out apps/geo_lift_sh.html
	$(CORE)/python apps/verify_geo_deck.py --deck apps/geo_lift_sh.html --allow-missing-slides

html-unified:  ## build the UNIFIED session deck (apps/unified_slides.html) — labs hook + short geo arc
	# Part 1 (real PyMC Labs engagements) in front of the short classical geo deck, one file.
	# Tokens from BOTH sources ({{labs.*}} pins + {{nb07*.*}} shards), one merged DATA bundle.
	# Edit apps/unified_slides_src.html, then rebuild. Narrative: apps/geo_lift_lecture_emphasis.md.
	$(CORE)/python apps/build_unified_slides.py
	$(CORE)/python apps/verify_unified_deck.py

site:  ## export the WASM-safe apps to static, in-browser pages under site/
	$(CORE)/marimo export html-wasm apps/experiment_design.py -o site/experiment_design --mode run
	$(CORE)/marimo export html-wasm apps/iv_lecture.py -o site/iv_lecture --mode run
	@echo "Serve locally:  python -m http.server --directory site"

warm:  ## RUN THIS BEFORE A LECTURE. Populates the fit cache so no notebook samples live.
	@echo "Warming the posterior cache (~/.cache/cmp/fits, or \$$CMP_CACHE_HOME)..."
	CMP_FAST=0 $(CORE)/python -m pytest tests/test_notebooks.py -q -x
	@$(CORE)/python -c "from cmp.cache import cache_info; \
	  rows = cache_info(); \
	  print(f'{len(rows)} fits cached, {sum(r[\"mb\"] for r in rows):.0f} MB total'); \
	  [print(f'  {r[\"file\"]:<48} {r[\"mb\"]:>6.1f} MB') for r in rows]"
	@echo "Cache warm. Notebooks will now LOAD their posteriors instead of re-sampling."

refit:  ## force every cached fit to recompute (use after changing a model)
	CMP_REFIT=1 CMP_FAST=0 $(CORE)/python -m pytest tests/test_notebooks.py -q

test:
	$(CORE)/python -m pytest tests/ -v

test-fast:
	$(CORE)/python -m pytest tests/test_package.py -v

test-legacy:  ## truth-recovery guards for the CausalPy DiD/ITS/IV estimators (legacy env)
	CMP_FAST=1 $(LEGACY)/python -m pytest tests/test_estimators_legacy.py -v

reports:  ## render one PDF per notebook (narrative + plots) into reports/ ; needs xelatex on PATH
	PATH="/Library/TeX/texbin:$$PATH" $(CORE)/python scripts/make_reports.py

book:  ## typeset the BOOK (book/build/book.pdf) + the chapter offprints, from the executed notebooks
	# Reads book/build/results.json, which the notebooks write via cmp.report when they run.
	# Numbers are injected as macros — nothing is retyped — so a missing one is a compile error.
	PATH="/Library/TeX/texbin:$$PATH" $(CORE)/python book/build.py

clean:
	rm -rf .pytest_cache notebooks/*.html site/
	find . -path './.venv*' -prune -o -name __pycache__ -type d -exec rm -rf {} +
