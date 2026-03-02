# Live R Parity Requirements

This test suite validates Python implementations directly against the live
Bioconductor `onlineFDR` package through `rpy2`.

## Mandatory Setup

1. Install development dependencies:

```bash
uv sync --group dev
```

2. Ensure a system R installation is available.
3. Install `onlineFDR` in R and pin it to version `2.18.0`.
4. Use R `4.5.x` (Bioconductor `3.22` requirement for `onlineFDR==2.18.0`).

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
sudo apt-get install -y libtirpc-dev
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
