"""
Geographic Risk Data

Python library for extracting HIFCA and HIDTA county-level geographic risk data.

Usage:
    from geo_risk_data import get_hifca, get_hidta, get_combined
    
    # Get HIFCA data only
    hifca_df = get_hifca()
    
    # Get HIDTA data only
    hidta_df = get_hidta()
    
    # Get combined data with flags
    combined_df = get_combined()
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

from .hifca import HIFCAScraper
from .hidta import HIDTAScraper
from .merger import merge_datasets
from .utils import setup_logging

import logging

# Setup default logging
logger = logging.getLogger(__name__)


def get_hifca(validate_layout=True, cache_dir=None):
    """
    Get HIFCA county-level data.
    
    Args:
        validate_layout: If True, validate source page layout before scraping
        cache_dir: Directory to cache layout snapshots (default: ~/.geo_risk_data)
        
    Returns:
        pandas.DataFrame with columns:
            - state_id: 2-letter state code
            - state_name: Full state name
            - county_fips: 5-digit FIPS code
            - county_name: County name
            - hifca_tier: Tier information (Tier I, Tier II, etc.)
            - source_url: Source data URL
            - last_extracted_date: Date data was extracted
            
    Raises:
        LayoutChangedError: If source page layout has changed significantly
        ValidationError: If data validation fails
    """
    
    logger.info("Fetching HIFCA data...")
    
    scraper = HIFCAScraper(validate_layout=validate_layout, cache_dir=cache_dir)
    df = scraper.scrape()
    
    logger.info(f"✓ Retrieved {len(df)} HIFCA counties")
    
    return df


def get_hidta(validate_layout=True, cache_dir=None):
    """
    Get HIDTA county-level data.
    
    Args:
        validate_layout: If True, validate source data before scraping
        cache_dir: Directory to cache layout snapshots
        
    Returns:
        pandas.DataFrame with columns:
            - state_id: 2-letter state code
            - state_name: Full state name
            - county_fips: 5-digit FIPS code
            - county_name: County name
            - source_url: Source data URL
            - last_extracted_date: Date data was extracted
            
    Raises:
        ValidationError: If data validation fails
    """
    
    logger.info("Fetching HIDTA data...")
    
    scraper = HIDTAScraper(validate_layout=validate_layout, cache_dir=cache_dir)
    df = scraper.scrape()
    
    logger.info(f"✓ Retrieved {len(df)} HIDTA counties")
    
    return df


def get_combined(validate_layout=True, cache_dir=None):
    """
    Get combined HIFCA and HIDTA data with designation flags.
    
    Args:
        validate_layout: If True, validate source layouts before scraping
        cache_dir: Directory to cache layout snapshots
        
    Returns:
        pandas.DataFrame with columns:
            - state_id, state_name, county_fips, county_name
            - hifca_flag: 1 if HIFCA, 0 otherwise
            - hidta_flag: 1 if HIDTA, 0 otherwise
            - hifca_hidta_flag: 'BOTH', 'HIFCA', 'HIDTA', or 'NONE'
            - hifca_tier: Tier information (for HIFCA counties)
            - source_url: Source data URL
            - last_extracted_date: Date data was extracted
            
    Raises:
        LayoutChangedError: If source page layouts have changed
        ValidationError: If data validation fails
    """
    
    logger.info("Fetching combined HIFCA and HIDTA data...")
    
    # Get both datasets
    hifca_df = get_hifca(validate_layout=validate_layout, cache_dir=cache_dir)
    hidta_df = get_hidta(validate_layout=validate_layout, cache_dir=cache_dir)
    
    # Merge
    combined_df = merge_datasets(hifca_df, hidta_df)
    
    logger.info(f"✓ Retrieved {len(combined_df)} total counties")
    logger.info(f"  HIFCA only: {len(combined_df[combined_df['hifca_hidta_flag'] == 'HIFCA'])}")
    logger.info(f"  HIDTA only: {len(combined_df[combined_df['hifca_hidta_flag'] == 'HIDTA'])}")
    logger.info(f"  Both: {len(combined_df[combined_df['hifca_hidta_flag'] == 'BOTH'])}")
    
    return combined_df


# Expose exceptions
from .validators import LayoutChangedError, ValidationError

__all__ = [
    'get_hifca',
    'get_hidta',
    'get_combined',
    'HIFCAScraper',
    'HIDTAScraper',
    'merge_datasets',
    'LayoutChangedError',
    'ValidationError',
]
