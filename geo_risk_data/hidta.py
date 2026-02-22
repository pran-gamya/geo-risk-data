"""
HIDTA data scraper
"""

import logging
import pandas as pd

from .utils import fetch_census_counties, create_county_dict
from .validators import validate_county_data

logger = logging.getLogger(__name__)


class HIDTAScraper:
    """
    Scraper for HIDTA (High Intensity Drug Trafficking Area) data.
    
    Extracts county-level HIDTA data from official designations.
    """
    
    SOURCE_URL = 'HIDTA Official Designations'  # No single URL, using official data
    
    # HIDTA regions (28 total) with county lists
    HIDTA_REGIONS = {
        'Appalachia': {
            'OH': ['Adams', 'Athens', 'Gallia', 'Jackson', 'Lawrence', 'Meigs', 'Pike', 'Ross', 'Scioto', 'Vinton'],
            'KY': ['Boyd', 'Carter', 'Elliott', 'Floyd', 'Greenup', 'Johnson', 'Lawrence', 'Martin', 'Pike'],
            'WV': ['Boone', 'Cabell', 'Lincoln', 'Logan', 'McDowell', 'Mercer', 'Mingo', 'Wayne', 'Wyoming'],
            'TN': ['Campbell', 'Claiborne', 'Cocke', 'Grainger', 'Greene', 'Hamblen', 'Hancock', 'Hawkins', 'Jefferson', 'Johnson', 'Scott', 'Sullivan', 'Unicoi', 'Union', 'Washington']
        },
        'Atlanta': {'GA': ['Bartow', 'Cherokee', 'Clayton', 'Cobb', 'DeKalb', 'Douglas', 'Fayette', 'Forsyth', 'Fulton', 'Gwinnett', 'Henry', 'Paulding', 'Rockdale']},
        'Central Florida': {'FL': ['Brevard', 'Flagler', 'Lake', 'Orange', 'Osceola', 'Polk', 'Seminole', 'Volusia']},
        'Chicago': {'IL': ['Cook', 'DuPage', 'Kane', 'Lake', 'McHenry', 'Will']},
        'Gulf Coast': {
            'AL': ['Mobile'],
            'MS': ['Hancock', 'Harrison', 'Jackson'],
            'LA': ['Jefferson', 'Orleans', 'Plaquemines', 'St. Bernard', 'St. Charles', 'St. James', 'St. John the Baptist', 'St. Tammany']
        },
        'Hawaii': {'HI': ['Hawaii', 'Honolulu', 'Kauai', 'Maui']},
        'Houston': {'TX': ['Brazoria', 'Chambers', 'Fort Bend', 'Galveston', 'Harris', 'Liberty', 'Montgomery', 'Waller']},
        'Los Angeles': {'CA': ['Los Angeles', 'Orange', 'Riverside', 'San Bernardino', 'Ventura']},
        'Midwest': {
            'IA': ['Polk', 'Scott'],
            'KS': ['Johnson', 'Wyandotte'],
            'MO': ['Buchanan', 'Cass', 'Clay', 'Jackson', 'Platte', 'St. Louis'],
            'NE': ['Douglas', 'Sarpy'],
            'ND': ['Cass', 'Grand Forks', 'Richland'],
            'SD': ['Lincoln', 'Minnehaha']
        },
        'Nevada': {'NV': ['Clark', 'Washoe']},
        'New England': {
            'CT': ['Fairfield', 'Hartford', 'New Haven'],
            'MA': ['Bristol', 'Essex', 'Hampden', 'Middlesex', 'Norfolk', 'Plymouth', 'Suffolk', 'Worcester'],
            'ME': ['Cumberland'],
            'NH': ['Hillsborough', 'Rockingham'],
            'RI': ['Kent', 'Providence'],
            'VT': ['Chittenden']
        },
        'New Mexico': {'NM': ['Bernalillo', 'Doña Ana', 'San Juan', 'Santa Fe']},
        'New York/New Jersey': {'NY': ['ALL'], 'NJ': ['ALL']},
        'North Florida': {'FL': ['Alachua', 'Baker', 'Bay', 'Bradford', 'Calhoun', 'Clay', 'Columbia', 'Dixie', 'Duval', 'Escambia', 'Franklin', 'Gadsden', 'Gilchrist', 'Gulf', 'Hamilton', 'Holmes', 'Jackson', 'Jefferson', 'Lafayette', 'Leon', 'Levy', 'Liberty', 'Madison', 'Nassau', 'Okaloosa', 'Santa Rosa', 'St. Johns', 'Suwannee', 'Taylor', 'Union', 'Wakulla', 'Walton', 'Washington']},
        'North Texas': {'TX': ['Collin', 'Dallas', 'Denton', 'Ellis', 'Johnson', 'Kaufman', 'Parker', 'Rockwall', 'Tarrant', 'Wise']},
        'Northwest': {'OR': ['Clackamas', 'Multnomah', 'Washington'], 'WA': ['King', 'Pierce', 'Snohomish']},
        'Oregon-Idaho': {'OR': ['Deschutes', 'Jackson', 'Lane', 'Marion'], 'ID': ['Ada', 'Canyon']},
        'Philadelphia': {'PA': ['Bucks', 'Chester', 'Delaware', 'Montgomery', 'Philadelphia'], 'NJ': ['Burlington', 'Camden', 'Gloucester']},
        'Puerto Rico': {'PR': ['ALL']},
        'South Florida': {'FL': ['Broward', 'Indian River', 'Martin', 'Miami-Dade', 'Monroe', 'Okeechobee', 'Palm Beach', 'St. Lucie']},
        'Southwest Border': {
            'CA': ['Imperial', 'San Diego'],
            'AZ': ['Cochise', 'Pima', 'Santa Cruz', 'Yuma'],
            'NM': ['Doña Ana', 'Grant', 'Hidalgo', 'Luna'],
            'TX': ['Brewster', 'Cameron', 'Culberson', 'Dimmit', 'El Paso', 'Hidalgo', 'Hudspeth', 'Jeff Davis', 'Kinney', 'La Salle', 'Maverick', 'Presidio', 'Starr', 'Terrell', 'Val Verde', 'Webb', 'Zapata']
        },
        'Washington/Baltimore': {
            'DC': ['ALL'],
            'MD': ['Anne Arundel', 'Baltimore', 'Carroll', 'Frederick', 'Harford', 'Howard', 'Montgomery', "Prince George's"],
            'VA': ['Arlington', 'Fairfax', 'Loudoun', 'Prince William']
        },
        'Wisconsin': {'WI': ['Brown', 'Dane', 'Kenosha', 'Milwaukee', 'Ozaukee', 'Racine', 'Washington', 'Waukesha']}
    }
    
    def __init__(self, validate_layout=True, cache_dir=None):
        """
        Initialize HIDTA scraper.
        
        Args:
            validate_layout: Not used for HIDTA (no web scraping)
            cache_dir: Not used for HIDTA
        """
        pass
    
    def scrape(self):
        """
        Extract HIDTA data.
        
        Returns:
            pandas.DataFrame with HIDTA county data
        """
        logger.info("Starting HIDTA extraction from official designations")
        
        all_counties = []
        region_stats = {}
        
        for region, states in self.HIDTA_REGIONS.items():
            logger.debug(f"Processing {region}...")
            region_count = 0
            
            
        for state_code, counties in states.items():
            
            if 'ALL' in counties:
                state_counties = fetch_census_counties(state_code)
                
                if len(state_counties) == 0:
                    logger.error(f"  {state_code}: FAILED to fetch counties (ALL)")
                else:
                    all_counties.extend(state_counties)
                    region_count += len(state_counties)
                    logger.info(f"  {state_code}: {len(state_counties)} counties (ALL)")
            
            else:
                state_counties = fetch_census_counties(state_code)
                
                if len(state_counties) == 0:
                    logger.error(f"  {state_code}: FAILED to fetch state counties")
                    continue
                
                county_map = {c['county_name'].lower(): c for c in state_counties}
                
                matched = 0
                for county_name in counties:
                    key = county_name.lower()
                    if key in county_map:
                        all_counties.append(county_map[key])
                        matched += 1
                    else:
                        logger.warning(f"  Could not find {county_name} in {state_code}")
                
                region_count += matched
                logger.info(f"  {state_code}: {matched}/{len(counties)} counties")
                    
            region_stats[region] = region_count
        
        # Create DataFrame
        df = pd.DataFrame(all_counties)
        df = df.drop_duplicates(subset=['county_fips'])
        
        # Validate
        validate_county_data(
            df,
            min_counties=600,
            expected_columns=['state_id', 'county_fips', 'county_name', 'source_url', 'last_extracted_date']
        )
        
        logger.info(f"✓ Extracted {len(df)} HIDTA counties from {len(self.HIDTA_REGIONS)} regions")
        logger.info(f"  Top regions: {sorted(region_stats.items(), key=lambda x: x[1], reverse=True)[:5]}")
        
        return df
