# Pre-Publish Checklist

Complete this checklist before publishing your package.

## ☐ Step 1: Customize Package Information

### Update setup.py
- [ ] Line 13: Replace "Your Name" with your actual name
- [ ] Line 14: Replace "your.email@example.com" with your email
- [ ] Line 19: Replace "yourusername" with your GitHub username

### Update LICENSE
- [ ] Line 3: Replace "[Your Name]" with your actual name

### Update README.md
- [ ] Search and replace "yourusername" with your GitHub username
- [ ] Update support email in Support section

## ☐ Step 2: Test Locally

```bash
# Install dependencies
pip install requests pandas beautifulsoup4 pytest black flake8

# Install package in development mode
cd /path/to/package
pip install -e .[dev]
```

- [ ] Installation successful (no errors)

```bash
# Run tests
pytest -v
```

- [ ] All tests pass (should see 10+ passing tests)

```bash
# Test CLI commands
geo-risk-data --hifca -o test_hifca.csv
```

- [ ] HIFCA extraction works (creates CSV with ~238 counties)

```bash
geo-risk-data --hidta -o test_hidta.csv
```

- [ ] HIDTA extraction works (creates CSV with ~700 counties)

```bash
geo-risk-data --both -o test_combined.csv
```

- [ ] Combined extraction works (creates CSV with ~900 counties)

```python
# Test Python API
from geo_risk_data import get_hifca, get_hidta, get_combined
hifca = get_hifca()
hidta = get_hidta()
combined = get_combined()
print(f"HIFCA: {len(hifca)}, HIDTA: {len(hidta)}, Combined: {len(combined)}")
```

- [ ] Python API works (prints counts)

## ☐ Step 3: Check Output Quality

Open test_combined.csv:
- [ ] Has columns: state_id, state_name, county_fips, county_name, hifca_flag, hidta_flag, hifca_hidta_flag, hifca_tier, source_url, last_extracted_date
- [ ] Has ~900 rows
- [ ] No null values in county_fips
- [ ] FIPS codes are 5 digits
- [ ] source_url column is populated
- [ ] last_extracted_date is today's date
- [ ] Some rows have hifca_tier = "Tier I"
- [ ] Some rows have hifca_tier = "Tier II"
- [ ] Some rows have hifca_hidta_flag = "BOTH"

## ☐ Step 4: Code Quality

```bash
# Format code
black geo_risk_data/
```

- [ ] Code formatted

```bash
# Check linting
flake8 geo_risk_data/ --max-line-length=100
```

- [ ] No major linting errors

## ☐ Step 5: Documentation

- [ ] README.md is complete and accurate
- [ ] CHANGELOG.md has version 1.0.0 entry
- [ ] All markdown files have no broken links
- [ ] Examples in README.md work

## ☐ Step 6: GitHub Setup

### Create GitHub Account
- [ ] Have GitHub account (or create at https://github.com/signup)
- [ ] Git is installed on your computer

### Create Repository
- [ ] Created new repo on GitHub named "geo-risk-data"
- [ ] Repo is Public (recommended)
- [ ] Did NOT initialize with README (we have our own)

### Initialize Local Git
```bash
cd /path/to/package
git init
git add .
git commit -m "Initial commit: geo-risk-data v1.0.0"
```

- [ ] Local git repo initialized
- [ ] All files committed

### Push to GitHub
```bash
git remote add origin https://github.com/YOURUSERNAME/geo-risk-data.git
git branch -M main
git push -u origin main
```

- [ ] Code pushed to GitHub
- [ ] Can see files at https://github.com/YOURUSERNAME/geo-risk-data

### Add Topics
On GitHub repo page, click ⚙️ next to "About":
- [ ] Added topics: python, data-extraction, geographic-data, bsa-aml, compliance, hifca, hidta

### Create Release
- [ ] Created release v1.0.0 on GitHub
- [ ] Added release notes

## ☐ Step 7: PyPI Publication

### Install Build Tools
```bash
pip install build twine
```

- [ ] Build tools installed

### Build Package
```bash
# Clean old builds
rm -rf build/ dist/ *.egg-info

# Build
python -m build
```

- [ ] Build successful
- [ ] dist/ directory created
- [ ] Contains .tar.gz and .whl files

### Test on TestPyPI (Optional)
```bash
# Create account at https://test.pypi.org/account/register/
python -m twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ geo-risk-data
```

- [ ] TestPyPI upload successful (optional)
- [ ] Test installation works (optional)

### Publish to Real PyPI
```bash
# Create account at https://pypi.org/account/register/
python -m twine upload dist/*
```

- [ ] PyPI upload successful
- [ ] Package visible at https://pypi.org/project/geo-risk-data/

### Test Installation
```bash
# In a new environment
pip install geo-risk-data
geo-risk-data --version
```

- [ ] Installation from PyPI works
- [ ] Command works

## ☐ Step 8: Final Checks

- [ ] GitHub repo has green checkmark (if CI/CD is set up)
- [ ] PyPI page shows correct version
- [ ] README renders correctly on both GitHub and PyPI
- [ ] Badge links work
- [ ] Can install and use package

## ☐ Step 9: Announce

- [ ] Star your own GitHub repo
- [ ] Share on LinkedIn
- [ ] Share on Twitter/X
- [ ] Add to your resume/portfolio

## ✅ You're Done!

Your package is published and ready for users!

Users can now:
```bash
pip install geo-risk-data
```

```python
from geo_risk_data import get_combined
df = get_combined()
```

## 🎉 Congratulations!

You've successfully:
- ✅ Built a production-ready Python package
- ✅ Published to GitHub
- ✅ Published to PyPI
- ✅ Made it available to the world

## 📊 Track Your Package

- **GitHub Stars**: https://github.com/YOURUSERNAME/geo-risk-data/stargazers
- **PyPI Downloads**: https://pypistats.org/packages/geo-risk-data
- **Issues**: https://github.com/YOURUSERNAME/geo-risk-data/issues

## 🔄 Next Update

When you have changes:

1. Make changes
2. Update version in setup.py (e.g., 1.0.0 → 1.1.0)
3. Update CHANGELOG.md
4. Commit and push to GitHub
5. Create new release on GitHub
6. Build and publish to PyPI:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

Good luck! 🚀
