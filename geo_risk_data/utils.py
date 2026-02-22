"""
Shared utilities for geo-risk-data package
"""

import requests
import logging
from datetime import datetime
from pathlib import Path

# State mappings
STATE_FIPS = {
    'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06', 'CO': '08',
    'CT': '09', 'DE': '10', 'FL': '12', 'GA': '13', 'HI': '15', 'ID': '16',
    'IL': '17', 'IN': '18', 'IA': '19', 'KS': '20', 'KY': '21', 'LA': '22',
    'ME': '23', 'MD': '24', 'MA': '25', 'MI': '26', 'MN': '27', 'MS': '28',
    'MO': '29', 'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33', 'NJ': '34',
    'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39', 'OK': '40',
    'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45', 'SD': '46', 'TN': '47',
    'TX': '48', 'UT': '49', 'VT': '50', 'VA': '51', 'WA': '53', 'WV': '54',
    'WI': '55', 'WY': '56', 'DC': '11', 'PR': '72', 'VI': '78'
}

STATE_NAMES = {code: name for name, code in {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC',
    'Puerto Rico': 'PR', 'Virgin Islands': 'VI'
}.items()}


def setup_logging(level=logging.INFO):
    """
    Setup logging configuration.
    
    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_cache_dir(cache_dir=None):
    """
    Get cache directory for layout snapshots.
    
    Args:
        cache_dir: Custom cache directory or None for default
        
    Returns:
        Path object for cache directory
    """
    if cache_dir:
        cache_path = Path(cache_dir)
    else:
        cache_path = Path.home() / '.geo_risk_data' / 'cache'
    
    cache_path.mkdir(parents=True, exist_ok=True)
    return cache_path


def fetch_census_counties(state_code, timeout=30):
    """
    Fetch all counties for a state from Census Bureau API.
    
    Args:
        state_code: 2-letter state code
        timeout: Request timeout in seconds
        
    Returns:
        List of dicts with county information
        
    Raises:
        requests.RequestException: If Census API request fails
    """
    logger = logging.getLogger(__name__)
    
    state_fips = STATE_FIPS.get(state_code)
    state_name = STATE_NAMES.get(state_code)
    
    if not state_fips:
        logger.warning(f"Unknown state code: {state_code}")
        return []
    
    url = f"https://api.census.gov/data/2020/dec/pl?get=NAME&for=county:*&in=state:{state_fips}"
    
    try:
        logger.debug(f"Fetching counties for {state_code} from Census API...")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Parse JSON with error handling
        try:
            data = response.json()
        except ValueError as e:
            logger.warning(f"Invalid JSON response for {state_code}: {str(e)}")
            logger.debug(f"Response content: {response.text[:200]}")
            return []
        
        counties = []
        
        for row in data[1:]:  # Skip header
            county_name = row[0].replace(' County', '').replace(' Parish', '')
            if ', ' + state_name in county_name:
                county_name = county_name.replace(', ' + state_name, '')
            
            county_fips = state_fips + row[2]
            
            counties.append({
                'state_id': state_code,
                'state_name': state_name,
                'county_fips': county_fips,
                'county_name': county_name
            })
        
        logger.debug(f"✓ Retrieved {len(counties)} counties for {state_code}")
        return counties
        
    except requests.RequestException as e:
        logger.warning(f"Census API request failed for {state_code}: {str(e)}")
        return []  # Return empty list instead of raising
    except (KeyError, IndexError) as e:
        logger.warning(f"Failed to parse Census API response for {state_code}: {str(e)}")
        return []
    
    
def get_current_date():
    """Get current date in YYYY-MM-DD format."""
    return datetime.now().strftime('%Y-%m-%d')


def fetch_url(url, timeout=30):
    """
    Fetch URL with error handling and logging.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        requests.Response object
        
    Raises:
        requests.RequestException: If request fails
    """
    logger = logging.getLogger(__name__)
    
    logger.debug(f"Fetching: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        logger.debug(f"✓ Fetched {len(response.content)} bytes")
        return response
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {str(e)}")
        raise


def create_county_dict(county_info, tier=None, source_url=None):
    """
    Create standardized county dictionary.
    
    Args:
        county_info: Base county info dict with state_id, county_fips, etc.
        tier: Optional tier information
        source_url: Optional source URL
        
    Returns:
        Dict with standardized fields
    """
    result = county_info.copy()
    
    if tier is not None:
        result['tier'] = tier
    
    if source_url:
        result['source_url'] = source_url
    
    result['last_extracted_date'] = get_current_date()
    
    return result
