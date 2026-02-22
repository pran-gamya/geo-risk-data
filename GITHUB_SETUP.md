# GitHub Setup and Publishing Guide

Complete guide to upload your `geo-risk-data` package to GitHub and publish to PyPI.

## Prerequisites

1. **GitHub account**: Create at https://github.com/signup
2. **Git installed**: Download from https://git-scm.com/
3. **Python 3.7+**: Installed on your system
4. **PyPI account** (for publishing): Create at https://pypi.org/account/register/

## Part 1: Initial Setup

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `geo-risk-data`
   - **Description**: "Python library for extracting HIFCA and HIDTA county-level geographic risk data"
   - **Public** or **Private**: Choose Public (recommended for open source)
   - **DO NOT** initialize with README (we already have one)
3. Click "Create repository"

### Step 2: Update Package Information

Before uploading, update these files with your information:

**`setup.py`:**
```python
author="Your Name",
author_email="your.email@example.com",
url="https://github.com/YOURUSERNAME/geo-risk-data",
```

**`LICENSE`:**
```
Copyright (c) 2026 Your Name
```

**`README.md`:**
- Replace `yourusername` in GitHub URLs
- Update support email

## Part 2: Upload to GitHub

### Step 3: Initialize Local Git Repository

Open terminal/command prompt in your package directory:

```bash
# Navigate to package directory
cd /path/to/package

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: geo-risk-data v1.0.0"
```

### Step 4: Connect to GitHub

Replace `YOURUSERNAME` with your GitHub username:

```bash
# Add remote repository
git remote add origin https://github.com/YOURUSERNAME/geo-risk-data.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**If authentication fails:**
- Use Personal Access Token (PAT) instead of password
- Create PAT at: https://github.com/settings/tokens
- Select scopes: `repo`, `workflow`
- Use PAT as password when prompted

### Step 5: Verify Upload

1. Go to `https://github.com/YOURUSERNAME/geo-risk-data`
2. You should see all your files
3. README.md should display automatically

## Part 3: Add GitHub Features

### Step 6: Add Topics

1. On your repository page, click the ⚙️ icon next to "About"
2. Add topics:
   - `python`
   - `data-extraction`
   - `geographic-data`
   - `bsa-aml`
   - `compliance`
   - `hifca`
   - `hidta`

### Step 7: Create Release

1. Go to your repo → "Releases" → "Create a new release"
2. Click "Choose a tag" → Type `v1.0.0` → "Create new tag"
3. Release title: `v1.0.0 - Initial Release`
4. Description:
   ```
   ## Features
   - HIFCA data extraction with tier information
   - HIDTA data extraction (28 regions)
   - Combined dataset with designation flags
   - Layout validation and change detection
   - Command-line interface
   - Python API
   
   ## Installation
   pip install geo-risk-data
   ```
5. Click "Publish release"

## Part 4: Publish to PyPI

### Step 8: Install Build Tools

```bash
# Install build tools
pip install build twine

# Install package in development mode
pip install -e .
```

### Step 9: Build Package

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build package
python -m build
```

This creates:
- `dist/geo-risk-data-1.0.0.tar.gz` (source distribution)
- `dist/geo_risk_data-1.0.0-py3-none-any.whl` (wheel)

### Step 10: Test on TestPyPI (Optional but Recommended)

```bash
# Create TestPyPI account at https://test.pypi.org/account/register/

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ geo-risk-data
```

### Step 11: Publish to PyPI

```bash
# Upload to real PyPI
python -m twine upload dist/*

# Enter your PyPI credentials when prompted
Username: YOUR_PYPI_USERNAME
Password: YOUR_PYPI_PASSWORD_OR_TOKEN
```

**Using API Token (Recommended):**
1. Go to https://pypi.org/manage/account/token/
2. Create token with scope: "Entire account"
3. Username: `__token__`
4. Password: `pypi-...` (your token)

### Step 12: Verify Publication

1. Go to https://pypi.org/project/geo-risk-data/
2. Your package should be live!
3. Test installation:
   ```bash
   pip install geo-risk-data
   ```

## Part 5: Add CI/CD with GitHub Actions

### Step 13: Create GitHub Workflow

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.7', '3.8', '3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=geo_risk_data
    
    - name: Check code formatting
      run: |
        black --check geo_risk_data/
```

Commit and push:
```bash
git add .github/workflows/tests.yml
git commit -m "Add CI/CD with GitHub Actions"
git push
```

## Part 6: Add Documentation Badge

### Step 14: Update README with Badges

Add to top of `README.md`:

```markdown
[![Tests](https://github.com/YOURUSERNAME/geo-risk-data/workflows/Tests/badge.svg)](https://github.com/YOURUSERNAME/geo-risk-data/actions)
[![PyPI version](https://badge.fury.io/py/geo-risk-data.svg)](https://badge.fury.io/py/geo-risk-data)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

## Part 7: Ongoing Maintenance

### Updating Your Package

When making changes:

```bash
# 1. Make your changes
# 2. Update version in setup.py (e.g., 1.0.0 → 1.1.0)
# 3. Update CHANGELOG.md

# 4. Commit changes
git add .
git commit -m "Add new feature X"
git push

# 5. Create new release on GitHub
# 6. Build and publish to PyPI
python -m build
python -m twine upload dist/*
```

### Versioning Guide

- **Major (1.0.0 → 2.0.0)**: Breaking changes
- **Minor (1.0.0 → 1.1.0)**: New features, backwards compatible
- **Patch (1.0.0 → 1.0.1)**: Bug fixes

## Quick Reference Commands

```bash
# Clone your repo
git clone https://github.com/YOURUSERNAME/geo-risk-data.git
cd geo-risk-data

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black geo_risk_data/

# Build package
python -m build

# Publish to PyPI
python -m twine upload dist/*

# Tag and push
git tag v1.0.0
git push origin v1.0.0
```

## Troubleshooting

### Issue: "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOURUSERNAME/geo-risk-data.git
```

### Issue: "Package already exists on PyPI"
- Update version in `setup.py`
- Rebuild: `python -m build`
- Upload: `python -m twine upload dist/*`

### Issue: "Permission denied (publickey)"
Use HTTPS instead of SSH, or set up SSH keys:
https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### Issue: Tests failing
```bash
# Run tests locally first
pytest -v

# Check specific test
pytest tests/test_geo_risk_data.py::TestHIFCA::test_hifca_extraction -v
```

## Support

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions
- **Pull Requests**: Contribute code

## Your Package is Live! 🎉

Now users can install with:
```bash
pip install geo-risk-data
```

And use it:
```python
from geo_risk_data import get_combined
df = get_combined()
```

**Next Steps:**
1. ⭐ Star your own repo to promote it
2. 📝 Add examples in a `examples/` directory
3. 📚 Create full documentation with Sphinx
4. 🐛 Fix any issues users report
5. 🚀 Promote on LinkedIn, Twitter, etc.
