# Contributing Guide

We welcome contributions to **online-fdr**! This guide will help you get started with contributing code, documentation, examples, or bug reports.

## Ways to Contribute

###  **Bug Reports**
- Report issues with existing functionality
- Include minimal reproducible examples
- Describe expected vs actual behavior

###  **Feature Requests**  
- Suggest new online FDR methods
- Propose API improvements
- Request documentation enhancements

###  **Code Contributions**
- Implement new methods from recent literature
- Fix bugs and improve performance
- Add tests and improve test coverage

###  **Documentation**
- Improve existing documentation
- Add examples and tutorials
- Fix typos and clarify explanations

###  **Examples and Tutorials**
- Real-world application examples
- Method comparison studies
- Educational content

## Getting Started

### Development Environment Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/online-fdr.git
   cd online-fdr
   ```

2. **Install Development Dependencies**
   ```bash
   pip install uv
   uv sync --group dev
   ```

3. **Install Local R Parity Prerequisites**
   `uv run pytest` includes mandatory live parity tests against R `onlineFDR`.

   **Shell note:** `apt-get`, `sudo`, `dpkg`, `ldconfig`, and `grep` are Linux
   commands. Run them in a Linux shell (WSL/Ubuntu), not Windows PowerShell.

   For Ubuntu/WSL, install R and build prerequisites:
   ```bash
   sudo apt-get update
   sudo apt-get install -y build-essential libffi-dev libtirpc-dev r-base r-base-dev
   ```

   For Windows-only setup, install R for Windows and ensure `R.exe`/`Rscript.exe`
   are on `PATH`, then continue with the `Rscript` commands below in PowerShell.

   Verify R is available:
   ```bash
   which R
   R --version
   R RHOME
   ```

   Ensure the R major/minor version is `4.5.x` (required by Bioconductor `3.22`).

   Install pinned `onlineFDR`:
   ```bash
   Rscript -e "if (!requireNamespace('BiocManager', quietly=TRUE)) install.packages('BiocManager', repos='https://cloud.r-project.org')"
   Rscript -e "BiocManager::install('onlineFDR', version='3.22', ask=FALSE, update=FALSE)"
   Rscript -e "stopifnot(as.character(utils::packageVersion('onlineFDR')) == '2.18.0')"
   ```

   If installation fails with:
   `Bioconductor version '3.22' requires R version '4.5'`,
   your local R is too old. Upgrade to R `4.5.x`, then rerun the install
   commands above.

4. **Install Pre-commit Hooks**
   ```bash
   uv run pre-commit install
   # or: pre-commit install
   ```

5. **Verify Installation**
   ```bash
   uv run pytest -q
   ```

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-method-name
   ```

2. **Make Changes**
   - Write code following our style guide
   - Add tests for new functionality
   - Update documentation as needed

3. **Run Tests and Checks**
   ```bash
   # Run tests
   uv run pytest
   
   # Check formatting
   uv run black --check online_fdr tests
   
   # Check linting  
   uv run ruff check online_fdr tests
   
   # Type checking
   uv run mypy online_fdr
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new LORD variant with decay"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/new-method-name
   ```
   Then create a pull request on GitHub.

## Code Style and Standards

### Formatting

We use **Black** for code formatting with these settings:
- Line length: 88 characters
- Target Python versions: 3.10+

```bash
# Format code
uv run black online_fdr tests

# Check formatting
uv run black --check online_fdr tests
```

### Linting

We use **Ruff** for fast Python linting:

```bash
# Run linting
uv run ruff check online_fdr tests

# Fix auto-fixable issues
uv run ruff check --fix online_fdr tests
```

### Type Hints

All new code should include type hints:

```python
from typing import List, Optional, Union

def test_one(self, p_value: float) -> bool:
    """
    Test a single p-value.
    
    Parameters
    ----------
    p_value : float
        P-value to test (0 <= p_value <= 1)
        
    Returns
    -------
    bool
        True if null hypothesis is rejected
    """
    pass
```

### Docstring Format

Use **NumPy-style docstrings**:

```python
def method_name(param1: float, param2: str = "default") -> bool:
    """
    Brief description of the method.
    
    Longer description explaining the method's purpose,
    algorithm, and usage context.
    
    Parameters
    ----------
    param1 : float
        Description of first parameter
    param2 : str, optional
        Description of second parameter, by default "default"
        
    Returns
    -------
    bool
        Description of return value
        
    Raises
    ------
    ValueError
        When parameters are invalid
        
    Examples
    --------
    >>> method = ClassName(alpha=0.05)
    >>> result = method.method_name(0.01, "custom")
    >>> print(result)
    True
    
    References
    ----------
    .. [1] Author, A. "Paper Title." Journal Name (Year).
    """
    pass
```

## Adding New Methods

### Method Implementation Structure

All sequential testing methods should inherit from `AbstractSequentialTest`:

```python
from online_fdr.core.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.core.utils import validity

class NewMethod(AbstractSequentialTest):
    """
    Implementation of NewMethod for online FDR control.
    
    This method implements the algorithm described in [1]_.
    
    Parameters
    ----------
    alpha : float
        Target FDR level (0 < alpha < 1)
    param1 : float
        Method-specific parameter
    param2 : float, optional
        Optional method-specific parameter, by default 0.5
        
    References
    ----------
    .. [1] Author, A. "NewMethod: Description." Journal (Year).
    """
    
    def __init__(self, alpha: float, param1: float, param2: float = 0.5):
        super().__init__(alpha)
        
        # Validate parameters
        validity.check_alpha(alpha)
        validity.check_param1(param1)  # Add custom validation
        
        # Store parameters
        self.param1 = param1
        self.param2 = param2
        
        # Initialize state
        self.num_tests = 0
        self.wealth = alpha * 0.5  # Example initialization
        
    def test_one(self, p_value: float) -> bool:
        """
        Test a single p-value.
        
        Parameters
        ----------
        p_value : float
            P-value to test (0 <= p_value <= 1)
            
        Returns
        -------
        bool
            True if null hypothesis is rejected
        """
        validity.check_p_val(p_value)
        
        self.num_tests += 1
        
        # Calculate current threshold
        self.alpha = self._calculate_threshold()
        
        if self.alpha is None or p_value > self.alpha:
            return False
            
        # Update state after rejection
        self._update_wealth()
        return True
        
    def _calculate_threshold(self) -> Optional[float]:
        """Calculate current significance threshold."""
        if self.wealth <= 0:
            return None
        # Implement threshold calculation
        return self.wealth * self.param1
        
    def _update_wealth(self) -> None:
        """Update wealth after a discovery."""
        self.wealth += self.param2  # Example wealth update
```

### Testing Requirements

Every new method requires comprehensive tests:

```python
# tests/test_new_method.py
import pytest
import numpy as np
from your_module_path import NewMethod  # replace with your implementation path
from online_fdr.core.utils.generation import DataGenerator, GaussianLocationModel

class TestNewMethod:
    """Test suite for NewMethod."""
    
    def test_initialization(self):
        """Test proper initialization."""
        method = NewMethod(alpha=0.05, param1=0.25)
        assert method.alpha0 == 0.05
        assert method.param1 == 0.25
        assert method.param2 == 0.5  # default
        
    def test_invalid_parameters(self):
        """Test parameter validation."""
        with pytest.raises(ValueError):
            NewMethod(alpha=1.5, param1=0.25)  # Invalid alpha
            
        with pytest.raises(ValueError):
            NewMethod(alpha=0.05, param1=-0.1)  # Invalid param1
            
    def test_single_p_value(self):
        """Test single p-value testing."""
        method = NewMethod(alpha=0.05, param1=0.25)
        
        # Should reject small p-value
        assert method.test_one(0.001) is True
        
        # Should not reject large p-value
        assert method.test_one(0.9) is False
        
    def test_fdr_control_simulation(self):
        """Test FDR control through simulation."""
        np.random.seed(42)
        
        method = NewMethod(alpha=0.1, param1=0.25)
        
        # Generate data with known null proportion
        dgp = GaussianLocationModel(alt_mean=2.0, alt_std=1.0, one_sided=True)
        generator = DataGenerator(n=1000, pi0=0.9, dgp=dgp)
        
        true_positives = false_positives = 0
        
        for _ in range(100):
            p_value, is_alternative = generator.sample_one()
            decision = method.test_one(p_value)
            
            if decision:
                if is_alternative:
                    true_positives += 1
                else:
                    false_positives += 1
        
        # Check FDR control
        total_discoveries = true_positives + false_positives
        if total_discoveries > 0:
            empirical_fdr = false_positives / total_discoveries
            assert empirical_fdr <= 0.15  # Allow some variance
            
    def test_wealth_dynamics(self):
        """Test wealth updates correctly."""
        method = NewMethod(alpha=0.05, param1=0.25)
        initial_wealth = method.wealth
        
        # Make a discovery
        method.test_one(0.01)
        
        # Wealth should have changed appropriately
        assert method.wealth != initial_wealth
        
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        method = NewMethod(alpha=0.05, param1=0.25)
        
        # Test p-value = 0
        result = method.test_one(0.0)
        assert isinstance(result, bool)
        
        # Test p-value = 1
        result = method.test_one(1.0)
        assert isinstance(result, bool)
        
        # Test when wealth is depleted
        method.wealth = 0.0
        assert method.test_one(0.001) is False
```

### Documentation Requirements

New methods need:

1. **API documentation** (docstrings in code)
2. **Usage examples** in docstrings
3. **Theoretical background** in theory section
4. **Practical examples** in examples section

### Performance Benchmarks

Include performance tests for new methods:

```python
def test_performance_benchmark(benchmark):
    """Benchmark method performance."""
    method = NewMethod(alpha=0.05, param1=0.25)
    p_values = np.random.uniform(0, 1, 1000)
    
    def run_tests():
        for p_val in p_values:
            method.test_one(p_val)
    
    benchmark(run_tests)
```

## Documentation Contributions

### Building Documentation Locally

```bash
cd docs
uv run mkdocs serve
# Open http://localhost:8000
```

### Documentation Structure

- `docs/index.md`: Home page
- `docs/installation.md`: Installation guide  
- `docs/quickstart.md`: Quick start tutorial
- `docs/user_guide/`: Detailed user guides
- `docs/api/`: API reference documentation
- `docs/examples/`: Practical examples
- `docs/theory/`: Mathematical theory
- `docs/contributing.md`: This file

### Writing Guidelines

- **Clear and concise**: Explain concepts simply
- **Code examples**: Include runnable examples  
- **Mathematical notation**: Use LaTeX for equations
- **Cross-references**: Link between sections
- **Accessibility**: Consider all skill levels

## Review Process

### Pull Request Guidelines

1. **Clear description**: Explain what and why
2. **Reference issues**: Link to related issues
3. **Tests included**: All new code needs tests
4. **Documentation updated**: Update relevant docs
5. **Changelog entry**: Add entry for user-facing changes

### Review Criteria

- **Functionality**: Does it work correctly?
- **Tests**: Adequate test coverage?  
- **Documentation**: Clear and complete?
- **Code quality**: Follows style guidelines?
- **Performance**: No significant regressions?

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)  
- **PATCH**: Bug fixes (backward compatible)

### Changelog

Update `CHANGELOG.md` for all user-facing changes:

```markdown
## [0.2.0] - 2024-01-15

### Added
- New LORD variant with memory decay
- Support for asynchronous testing

### Changed  
- Improved ADDIS parameter validation
- Updated documentation structure

### Fixed
- Bug in wealth calculation for edge case
- Typo in SAFFRON documentation
```

## Getting Help

### Community Resources

- **GitHub Discussions**: Ask questions, share ideas
- **GitHub Issues**: Report bugs, request features
- **Documentation**: Comprehensive guides and references

### Maintainer Contact

- **Primary maintainer**: Oliver Hennhfer
- **GitHub**: [@OliverHennhoefer](https://github.com/OliverHennhoefer)
- **Email**: oliver.hennhoefer@mail.de

### Communication Guidelines

- **Be respectful**: Follow our code of conduct
- **Be specific**: Include details, code examples, error messages
- **Be patient**: Maintainers are volunteers
- **Search first**: Check existing issues and discussions

## Recognition

Contributors will be:

- Listed in `CONTRIBUTORS.md`
- Mentioned in release notes for significant contributions
- Added as co-authors on academic papers when appropriate

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. All contributors are expected to:

- **Be respectful** of different viewpoints and experiences
- **Accept constructive criticism** gracefully  
- **Focus on what's best** for the community
- **Show empathy** towards other community members

## Quick Reference

### Common Commands

```bash
# Set up development environment
uv sync --group dev
uv run pre-commit install

# Local R parity setup (Ubuntu/WSL)
# Run these in a Linux shell, not Windows PowerShell
sudo apt-get update
sudo apt-get install -y build-essential libffi-dev libtirpc-dev r-base r-base-dev
Rscript -e "if (!requireNamespace('BiocManager', quietly=TRUE)) install.packages('BiocManager', repos='https://cloud.r-project.org')"
Rscript -e "BiocManager::install('onlineFDR', version='3.22', ask=FALSE, update=FALSE)"
Rscript -e "stopifnot(as.character(utils::packageVersion('onlineFDR')) == '2.18.0')"

# Run tests
uv run pytest -q
uv run pytest tests/test_specific.py -v

# Check code quality
uv run black online_fdr tests
uv run ruff check online_fdr tests  
uv run mypy online_fdr

# Build documentation
cd docs && uv run mkdocs serve

# Run specific test category
uv run pytest -m "not slow"
uv run pytest tests/ -k "test_fdr_control"
```

### File Naming Conventions

- **Source files**: `snake_case.py`
- **Test files**: `test_module_name.py`  
- **Documentation**: `kebab-case.md`
- **Examples**: `descriptive_example_name.py`

Thank you for contributing to **online-fdr**! Your efforts help advance the field of online multiple testing and benefit researchers worldwide. 

