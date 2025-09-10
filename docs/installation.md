# Installation

## Requirements

**online-fdr** requires Python 3.8 or higher and has minimal dependencies:

- `numpy >= 1.20.0`
- `scipy >= 1.9.0`

## Install from PyPI (Recommended)

The easiest way to install **online-fdr** is using pip:

```bash
pip install online-fdr
```

### Install with Optional Dependencies

For development and extended functionality:

=== "Development Dependencies"
    ```bash
    pip install online-fdr[dev]
    ```
    Includes testing, linting, and type checking tools:
    - `pytest >= 7.0`
    - `pytest-cov >= 4.0` 
    - `black >= 23.0`
    - `ruff >= 0.1.0`
    - `mypy >= 1.0`

=== "Documentation Dependencies"
    ```bash
    pip install online-fdr[docs]
    ```
    For building documentation locally:
    - `sphinx >= 5.0`
    - `sphinx-rtd-theme >= 1.0`
    - `myst-parser >= 0.18`

=== "All Dependencies"
    ```bash
    pip install online-fdr[dev,docs]
    ```

## Install from Source

For the latest development version or to contribute:

### Using Git

```bash
git clone https://github.com/OliverHennhoefer/online-fdr.git
cd online-fdr
pip install -e .
```

### Using uv (Recommended for Development)

[uv](https://github.com/astral-sh/uv) provides faster and more reliable dependency management:

```bash
# Install uv if you haven't already
pip install uv

# Clone and install
git clone https://github.com/OliverHennhoefer/online-fdr.git
cd online-fdr
uv sync --all-extras
```

### Development Setup

For contributors, set up a complete development environment:

```bash
git clone https://github.com/OliverHennhoefer/online-fdr.git
cd online-fdr

# Install with development dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Run tests to verify installation
uv run pytest
```

## Verify Installation

Test your installation by running:

```python
import online_fdr
from online_fdr.investing.addis.addis import Addis

# Create a simple test
addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
result = addis.test_one(0.01)
print(f"ADDIS test result: {result}")  # Should print: True
print(f"Package version: {online_fdr.__version__}")
```

## Troubleshooting

### Common Issues

!!! bug "Import Error: No module named 'online_fdr'"
    - Ensure you've activated the correct virtual environment
    - Try reinstalling: `pip uninstall online-fdr && pip install online-fdr`

!!! bug "numpy/scipy Version Conflicts"
    - Update your dependencies: `pip install --upgrade numpy scipy`
    - For conda users: `conda update numpy scipy`

!!! bug "Permission Denied During Installation"
    - Use a virtual environment: `python -m venv venv && source venv/bin/activate`
    - Or install for current user only: `pip install --user online-fdr`

### Platform-Specific Notes

=== "Windows"
    - Use PowerShell or Command Prompt
    - If using Anaconda, activate your environment first:
      ```cmd
      conda activate your_env_name
      pip install online-fdr
      ```

=== "macOS"
    - Xcode command line tools may be required for compiling dependencies
    - Install with: `xcode-select --install`

=== "Linux"
    - Most distributions work out of the box
    - For older systems, ensure you have a recent Python version

### Virtual Environments

We strongly recommend using virtual environments to avoid dependency conflicts:

=== "venv (Built-in)"
    ```bash
    python -m venv online-fdr-env
    source online-fdr-env/bin/activate  # Linux/macOS
    # or
    online-fdr-env\Scripts\activate  # Windows
    pip install online-fdr
    ```

=== "conda"
    ```bash
    conda create -n online-fdr python=3.11
    conda activate online-fdr
    pip install online-fdr
    ```

=== "Poetry"
    ```bash
    poetry new my-project
    cd my-project
    poetry add online-fdr
    poetry shell
    ```

## Next Steps

Once installed successfully:

1. 📚 **Read the [Quick Start Guide](quickstart.md)** for your first online FDR experiment
2. 🔍 **Browse [Examples](examples/index.md)** to see real-world applications  
3. 📖 **Explore [API Documentation](api/index.md)** for detailed method references
4. 🧮 **Study [Theory](theory/index.md)** to understand the mathematical foundations

## Need Help?

- 📋 **Check existing issues**: [GitHub Issues](https://github.com/OliverHennhoefer/online-fdr/issues)
- 💬 **Ask questions**: [GitHub Discussions](https://github.com/OliverHennhoefer/online-fdr/discussions)  
- 🐛 **Report bugs**: [Submit a new issue](https://github.com/OliverHennhoefer/online-fdr/issues/new)