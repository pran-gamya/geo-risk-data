# Geographic Risk Data

Python library for extracting HIFCA (High Intensity Financial Crime Area) and HIDTA (High Intensity Drug Trafficking Area) county-level geographic risk data from official sources.

[![PyPI version](https://badge.fury.io/py/geo-risk-data.svg)](https://badge.fury.io/py/geo-risk-data)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- ✅ **HIFCA Data**: Extract all 238 HIFCA counties with tier information (Tier I, Tier II, etc.)
- ✅ **HIDTA Data**: Extract all 700+ HIDTA counties across 28 regions
- ✅ **Combined Dataset**: Merge both with designation flags
- ✅ **Layout Validation**: Detect when source pages change
- ✅ **Source URLs**: Track data sources for auditability
- ✅ **CLI Tool**: Command-line interface for easy extraction
- ✅ **Python API**: Use as a library in your code

## Installation

```bash
# Basic installation
pip install geo-risk-data

# With PDF parsing support (recommended for HIFCA tier extraction)
pip install geo-risk-data[pdf]

# Development installation
pip install geo-risk-data[dev]
```

## Quick Start

### Command Line

```bash
# Get HIFCA data only
geo-risk-data --hifca --output hifca_counties.csv

# Get HIDTA data only
geo-risk-data --hidta --output hidta_counties.csv

# Get combined data
geo-risk-data --both --output combined.csv

# Skip layout validation (faster)
geo-risk-data --both --no-validate --output combined.csv
```

### Python API

```python
from geo_risk_data import get_hifca, get_hidta, get_combined

# Get HIFCA data
hifca_df = get_hifca()
print(f"HIFCA counties: {len(hifca_df)}")

# Get HIDTA data
hidta_df = get_hidta()
print(f"HIDTA counties: {len(hidta_df)}")

# Get combined data with flags
combined_df = get_combined()

# Find counties in both HIFCA and HIDTA
both = combined_df[combined_df['hifca_hidta_flag'] == 'BOTH']
print(f"Counties in both: {len(both)}")

# Get Tier I Southwest Border counties
tier1 = combined_df[combined_df['hifca_tier'] == 'Tier I']
print(tier1[['state_id', 'county_name', 'hifca_tier']])
```

## Output Format

### HIFCA Data

```csv
state_id,state_name,county_fips,county_name,hifca_tier,source_url,last_extracted_date
TX,Texas,48061,Cameron,Tier I,https://www.fincen.gov/hifca-regional-map,2026-02-21
TX,Texas,48489,Willacy,Tier II,https://www.fincen.gov/hifca-regional-map,2026-02-21
CA,California,06075,San Francisco,Northern District,https://www.fincen.gov/hifca-regional-map,2026-02-21
```

### HIDTA Data

```csv
state_id,state_name,county_fips,county_name,source_url,last_extracted_date
GA,Georgia,13067,Clayton,HIDTA Official Designations,2026-02-21
IL,Illinois,17031,Cook,HIDTA Official Designations,2026-02-21
```

### Combined Data

```csv
state_id,state_name,county_fips,county_name,hifca_flag,hidta_flag,hifca_hidta_flag,hifca_tier,source_url,last_extracted_date
TX,Texas,48061,Cameron,1,1,BOTH,Tier I,https://www.fincen.gov/hifca-regional-map,2026-02-21
GA,Georgia,13067,Clayton,0,1,HIDTA,,HIDTA Official Designations,2026-02-21
```

## Data Sources

- **HIFCA**: [FinCEN HIFCA Regional Map](https://www.fincen.gov/hifca-regional-map)
  - Includes Southwest Border PDF for tier information
  - ~238 counties across 9 regions
  
- **HIDTA**: Official HIDTA designations from ONDCP/HIDTA.gov
  - 28 HIDTA regions
  - ~700 counties

- **County FIPS Codes**: [US Census Bureau API](https://api.census.gov/)

## Layout Validation

The library includes automatic layout validation to detect when source pages change:

```python
from geo_risk_data import get_hifca
from geo_risk_data.validators import LayoutChangedError

try:
    df = get_hifca(validate_layout=True)
except LayoutChangedError as e:
    print(f"Source page changed: {e}")
    # Review changes and update code if needed
```

When a layout change is detected, the library:
1. Logs all changes (table count, PDF links, etc.)
2. Saves new layout as baseline
3. Raises exception if changes are significant
4. Allows you to skip validation with `validate_layout=False`

## CLI Usage

```bash
# Full help
geo-risk-data --help

# HIFCA only
geo-risk-data --hifca -o hifca.csv

# HIDTA only
geo-risk-data --hidta -o hidta.csv

# Combined (both)
geo-risk-data --both -o combined.csv

# Verbose logging
geo-risk-data --both -v -o combined.csv

# Skip validation
geo-risk-data --both --no-validate -o combined.csv

# Custom cache directory
geo-risk-data --both --cache-dir ./cache -o combined.csv
```

## Use Cases

### BSA/AML Compliance

```python
from geo_risk_data import get_combined

# Get combined data
df = get_combined()

# Assign risk scores
df['risk_score'] = df.apply(lambda row:
    10 if row['hifca_hidta_flag'] == 'BOTH' and row['hifca_tier'] == 'Tier I' else
    8 if row['hifca_tier'] == 'Tier I' else
    7 if row['hifca_tier'] == 'Tier II' else
    6 if row['hifca_hidta_flag'] == 'BOTH' else
    4 if row['hifca_flag'] == 1 else
    3 if row['hidta_flag'] == 1 else
    0,
    axis=1
)

# High risk counties
high_risk = df[df['risk_score'] >= 8]
print(f"High risk counties: {len(high_risk)}")
```

### Customer Risk Rating

```python
import pandas as pd
from geo_risk_data import get_combined

# Get geographic risk data
geo_risk = get_combined()

# Load customer data with ZIP codes
customers = pd.read_csv('customers.csv')

# Load ZIP to county crosswalk (HUD-USPS)
zip_crosswalk = pd.read_csv('zip_county_crosswalk.csv')

# Join customers -> ZIP -> county -> risk
customer_risk = customers.merge(
    zip_crosswalk, on='zip_code'
).merge(
    geo_risk, on='county_fips'
)

# Score customers
customer_risk['geo_risk_score'] = customer_risk['hifca_hidta_flag'].map({
    'BOTH': 3,
    'HIFCA': 2,
    'HIDTA': 2,
    'NONE': 0
})
```

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/geo-risk-data.git
cd geo-risk-data

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black geo_risk_data/

# Lint
flake8 geo_risk_data/
```

## Testing

```python
import pytest
from geo_risk_data import get_hifca, get_hidta, get_combined

def test_hifca_extraction():
    df = get_hifca(validate_layout=False)
    assert len(df) > 200  # At least 200 HIFCA counties
    assert 'hifca_tier' in df.columns
    assert 'source_url' in df.columns

def test_hidta_extraction():
    df = get_hidta(validate_layout=False)
    assert len(df) > 600  # At least 600 HIDTA counties
    assert 'state_id' in df.columns

def test_combined():
    df = get_combined(validate_layout=False)
    assert len(df) > 800  # At least 800 total counties
    assert 'hifca_hidta_flag' in df.columns
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This library extracts publicly available data from official government sources (FinCEN, ONDCP). It is provided for informational purposes only. Users are responsible for verifying data accuracy and ensuring compliance with applicable regulations.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/geo-risk-data/issues)
- **Documentation**: [Full Documentation](https://geo-risk-data.readthedocs.io/)
- **Email**: your.email@example.com

## Changelog

### Version 1.0.0 (2026-02-21)

- ✨ Initial release
- ✅ HIFCA extraction with tier information
- ✅ HIDTA extraction (28 regions)
- ✅ Combined dataset with flags
- ✅ Layout validation and change detection
- ✅ Command-line interface
- ✅ Python API

## Acknowledgments

- FinCEN for HIFCA data
- ONDCP for HIDTA data
- US Census Bureau for county FIPS codes
