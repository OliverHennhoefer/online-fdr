# Live R Parity Requirements

This test suite validates Python implementations directly against the live
Bioconductor `onlineFDR` package through `rpy2`.

## Mandatory Setup

1. Install R `4.5.x` and verify it is available from your shell:

   ```bash
   R --version
   Rscript --version
   ```

   macOS users can install R from CRAN or Homebrew. Windows users should install
   R for Windows, ensure `Rscript.exe` is on `PATH`, and run the commands below
   in PowerShell. Ubuntu/WSL users should install R `4.5.x`; if `rpy2` needs
   native build libraries, install `build-essential libffi-dev libtirpc-dev
   r-base-dev`.

2. Install development dependencies:

   ```bash
   uv sync --group dev
   ```

3. Install pinned Bioconductor `onlineFDR`:

   ```bash
   Rscript -e "options(repos = c(CRAN = 'https://cloud.r-project.org')); if (!requireNamespace('BiocManager', quietly = TRUE)) install.packages('BiocManager')"
   Rscript -e "BiocManager::install(version = '3.22', ask = FALSE, update = FALSE)"
   Rscript -e "BiocManager::install('onlineFDR', version = '3.22', ask = FALSE, update = FALSE)"
   Rscript -e "stopifnot(as.character(utils::packageVersion('onlineFDR')) == '2.18.0')"
   ```

4. Verify live parity:

   ```bash
   uv run pytest tests/test_onlinefdr_parity.py tests/test_async_methods.py -q
   ```

If `rpy2`, R, or `onlineFDR` are missing, parity tests fail with setup
instructions. These checks are not optional.

**Shell note:** Linux commands such as `apt-get`, `sudo`, `dpkg`, `ldconfig`,
and `grep` must be run in a Linux shell (for example WSL/Ubuntu), not in
Windows PowerShell.

### Ubuntu/WSL Note

If `rpy2` fails to build with linker errors like `cannot find -ltirpc`,
install the missing system development library:

```bash
sudo apt-get update
sudo apt-get install -y libtirpc-dev r-base-dev
```

If BiocManager reports:
`Bioconductor version '3.22' requires R version '4.5'`,
upgrade local R to `4.5.x` before installing `onlineFDR`.

## CI Execution

GitHub Actions runs the entire test suite (including live R parity tests) in a
containerized environment via:

- `.github/workflows/tests-container.yml`

The workflow uses a container with R preinstalled, installs pinned
`onlineFDR==2.18.0`, then runs `uv run python -m pytest -q`.
