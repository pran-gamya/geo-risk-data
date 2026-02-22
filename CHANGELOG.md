# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-21

### Added
- Initial release of geo-risk-data package
- HIFCA data extraction with tier information (Tier I, Tier II, Northern District, Southern District, State-wide)
- HIDTA data extraction covering all 28 HIDTA regions
- Combined dataset with designation flags (BOTH, HIFCA, HIDTA)
- Layout validation to detect source page changes
- Change detection with severity levels (HIGH, MEDIUM, LOW)
- Layout snapshot caching for future comparisons
- Command-line interface with --hifca, --hidta, --both options
- Python API with get_hifca(), get_hidta(), get_combined()
- Source URL tracking for auditability
- Last extraction date tracking
- Comprehensive logging with DEBUG, INFO, WARNING, ERROR levels
- Data validation (minimum county counts, FIPS format, null checks)
- Census Bureau API integration for county FIPS codes
- PDF parsing support for Southwest Border tier extraction (optional pdfplumber dependency)
- Fallback data for when web sources are unavailable
- Complete test suite with pytest
- MIT License
- Full documentation in README.md

### Features
- Extract ~238 HIFCA counties
- Extract ~700 HIDTA counties
- Merge into ~900 total counties with overlap detection
- Southwest Border tier classification (13 Tier I + 11 Tier II counties in TX)
- Arizona state-wide HIFCA designation (15 counties)
- California district separation (Northern: 14 counties, Southern: 7 counties)
- "All counties" states: NY (62), NJ (21), PR (78), VI (3)
- Chicago region (6 counties)
- South Florida region (8 counties)
- 28 HIDTA regions fully covered

### Technical
- Python 3.7+ support
- Pandas for data manipulation
- BeautifulSoup4 for HTML parsing
- Requests for HTTP operations
- Optional pdfplumber for PDF text extraction
- Layout validation with SHA256 hashing
- Caching in ~/.geo_risk_data/cache
- Console script entry point: `geo-risk-data`

### Data Sources
- FinCEN HIFCA Regional Map: https://www.fincen.gov/hifca-regional-map
- FinCEN Southwest Border PDF: https://www.fincen.gov/system/files/shared/southernborder.pdf
- HIDTA: Official ONDCP designations
- Census Bureau API: https://api.census.gov/data/2020/dec/pl

## [Unreleased]

### Planned
- Add historical data tracking (SCD Type 2)
- Add ZIP code crosswalk integration
- Add risk scoring examples
- Add Jupyter notebook examples
- Add data export to JSON, Excel formats
- Add API endpoint (Flask/FastAPI)
- Add dashboard visualization
- Add automated change notifications
- Improve PDF parsing accuracy
- Add more granular tier information
- Add effective date tracking
- Add removal history tracking

---

## Version History

### Versioning Scheme
- **Major.Minor.Patch** (e.g., 1.0.0)
- **Major**: Breaking changes
- **Minor**: New features, backwards compatible
- **Patch**: Bug fixes, minor improvements

### Release Notes Format
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be-removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes
