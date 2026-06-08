# Troubleshooting

This page collects common setup and runtime issues for `online-fdr`.

## `rpy2` and R Parity Issues

Parity tests require:

- `rpy2` installed in the active environment
- R available on `PATH`
- Bioconductor `onlineFDR` pinned to `2.18.0`
- R `4.5.x` (for Bioconductor `3.22`)

### Symptom: `R` or `Rscript` not found

Check runtime availability:

```bash
R --version
Rscript --version
```

If unavailable, install R and ensure executables are on `PATH`.

### Symptom: Bioconductor/R version mismatch

Example error:

`Bioconductor version '3.22' requires R version '4.5'`

Fix by upgrading to R `4.5.x`, then reinstalling:

```bash
Rscript -e "options(repos = c(CRAN = 'https://cloud.r-project.org')); if (!requireNamespace('BiocManager', quietly = TRUE)) install.packages('BiocManager')"
Rscript -e "BiocManager::install(version = '3.22', ask = FALSE, update = FALSE)"
Rscript -e "BiocManager::install('onlineFDR', version = '3.22', ask = FALSE, update = FALSE)"
Rscript -e "stopifnot(as.character(utils::packageVersion('onlineFDR')) == '2.18.0')"
```

### Symptom: Linux build error with missing `tirpc`

If `rpy2` build fails with linker errors such as `cannot find -ltirpc`, install:

```bash
sudo apt-get update
sudo apt-get install -y libtirpc-dev
```

Then reinstall dependencies.

## Import Errors

### Symptom: `ModuleNotFoundError: No module named 'online_fdr'`

Install package dependencies and run from repository root:

```bash
uv sync --group dev
uv run python -c "import online_fdr; print(online_fdr.__version__)"
```

## Test Selection Problems

### Symptom: full test run fails locally because R parity setup is incomplete

Run core suite first while completing R setup:

```bash
uv run python -m pytest -q --ignore=tests/test_onlinefdr_parity.py --ignore=tests/test_async_methods.py
```

After R setup is complete, run:

```bash
uv run python -m pytest tests/test_onlinefdr_parity.py tests/test_async_methods.py -q
```

## Documentation Build Issues

### Symptom: `mkdocs` command not found

Install docs dependencies:

```bash
uv sync --group docs --no-dev
```

Then run:

```bash
uv run mkdocs build --strict
```
