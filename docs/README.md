# Online FDR Documentation

This directory contains the complete documentation for the **online-fdr** package, built using [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Building the Documentation

### Local Development

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Serve documentation locally (with auto-reload)
cd docs
mkdocs serve

# Open http://localhost:8000 in your browser
```

### Building for Production

```bash
cd docs
mkdocs build --strict

# Output will be in ../site/ directory
```

## Documentation Structure

```
docs/
 mkdocs.yml                 # MkDocs configuration
 index.md                   # Home page
 installation.md            # Installation guide
 quickstart.md             # Quick start tutorial
 user_guide/               # Detailed user guides
    index.md              # User guide overview
    concepts.md           # Core concepts
    sequential.md         # Sequential methods
    batch.md              # Batch methods
    data_generation.md    # Data generation
    evaluation.md         # Performance evaluation
 api/                      # API reference
    index.md              # API overview
    investing/            # Alpha investing methods
    spending/             # Alpha spending methods  
    batching/             # Batch methods
    utils/                # Utilities
 examples/                 # Practical examples
    index.md              # Examples overview
    basic_usage.md        # Basic examples
    advanced.md           # Advanced scenarios
    comparison.md         # Method comparisons
 theory/                   # Mathematical theory
    index.md              # Theory overview
    fdr_control.md        # FDR control theory
    algorithms.md         # Algorithm details
    guarantee_matrix.md   # Method guarantee matrix
 contributing.md           # Contribution guide
 javascripts/              # Custom JavaScript
    mathjax.js           # MathJax configuration
 includes/                 # Snippets and abbreviations
     mkdocs.md            # Abbreviation definitions
```

## Features

- **Material Design**: Modern, responsive theme
- **Search**: Full-text search functionality
- **Code Highlighting**: Syntax highlighting for Python
- **Math Rendering**: LaTeX equations via MathJax
- **API Documentation**: Auto-generated from docstrings
- **Dark/Light Mode**: Toggle between themes
- **Mobile Responsive**: Works on all devices
- **Fast Loading**: Optimized for performance

## Deployment

Documentation is automatically built and deployed to GitHub Pages via GitHub Actions when changes are pushed to the main branch.

The workflow is defined in `.github/workflows/docs.yml`.

## Contributing

To contribute to the documentation:

1. Edit the relevant Markdown files
2. Test locally with `mkdocs serve`
3. Submit a pull request

See [Contributing Guide](contributing.md) for detailed guidelines.

## Configuration

Key configuration options in `mkdocs.yml`:

- **Theme**: Material for MkDocs with custom colors
- **Plugins**: Search, API docs, social cards, git revision dates
- **Extensions**: Admonitions, code highlighting, math rendering
- **Navigation**: Hierarchical structure with clear categories

For detailed configuration options, see the [MkDocs Material documentation](https://squidfunk.github.io/mkdocs-material/).
