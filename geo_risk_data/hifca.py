"""
HIFCA data scraper with layout validation
"""

import logging
import pandas as pd
from bs4 import BeautifulSoup
import io

from .utils import (
    fetch_census_counties, get_current_date, fetch_url,
    create_county_dict, get_cache_dir
)
from .validators import LayoutValidator, validate_county_data

logger = logging.getLogger(__name__)


class HIFCAScraper:
    """
    Scraper for HIFCA (High Intensity Financial Crime Area) data.
    
    Extracts county-level HIFCA data from FinCEN with tier information.
    """
    
    SOURCE_URL = 'https://www.fincen.gov/hifca-regional-map'
    SW_BORDER_PDF_URL = 'https://www.fincen.gov/system/files/shared/southernborder.pdf'
    
    def __init__(self, validate_layout=True, cache_dir=None):
        """
        Initialize HIFCA scraper.
        
        Args:
            validate_layout: If True, validate page layout before scraping
            cache_dir: Directory for layout cache
        """
        self.validate_layout = validate_layout
        self.cache_dir = get_cache_dir(cache_dir)
        self.validator = LayoutValidator(self.cache_dir) if validate_layout else None
    
    def scrape(self):
        """
        Scrape HIFCA data.
        
        Returns:
            pandas.DataFrame with HIFCA county data
        """
        logger.info(f"Starting HIFCA extraction from {self.SOURCE_URL}")
        
        all_counties = []
        
        # Fetch and validate main page
        response = fetch_url(self.SOURCE_URL)
        
        if self.validate_layout:
            logger.info("Validating page layout...")
            self.validator.validate_layout(response.text, self.SOURCE_URL)
        
        # Extract PDF URLs from page
        pdf_urls = self._extract_pdf_urls(response.text)
        logger.info(f"Found {len(pdf_urls)} PDF links on page")
        
        # Get Southwest Border data with tiers
        logger.info("Processing Southwest Border counties...")
        sw_data = self._get_sw_border_data(pdf_urls)
        
        # Arizona
        for county_name, tier in sw_data.get('AZ', {}).items():
            counties = fetch_census_counties('AZ')
            for c in counties:
                if c['county_name'] == county_name:
                    county = create_county_dict(
                        c, tier=tier, source_url=self.SOURCE_URL
                    )
                    all_counties.append(county)
                    logger.debug(f"  AZ: {county_name} ({tier})")
        
        # Texas
        for county_name, tier in sw_data.get('TX', {}).items():
            counties = fetch_census_counties('TX')
            for c in counties:
                if c['county_name'] == county_name:
                    county = create_county_dict(
                        c, tier=tier, source_url=self.SOURCE_URL
                    )
                    all_counties.append(county)
                    logger.debug(f"  TX: {county_name} ({tier})")
        
        # California districts
        logger.info("Processing California districts...")
        all_counties.extend(self._get_california_counties())
        
        # Other regions
        logger.info("Processing other HIFCA regions...")
        all_counties.extend(self._get_other_regions())
        
        # Create DataFrame
        df = pd.DataFrame(all_counties)
        df = df.drop_duplicates(subset=['county_fips'])
        
        # Validate extracted data
        validate_county_data(
            df,
            min_counties=200,
            expected_columns=['state_id', 'county_fips', 'county_name', 'source_url', 'last_extracted_date']
        )
        
        logger.info(f"✓ Extracted {len(df)} HIFCA counties")
        
        # Log tier breakdown
        if 'hifca_tier' in df.columns:
            tier_counts = df['hifca_tier'].value_counts(dropna=False)
            logger.info(f"  Tier breakdown: {tier_counts.to_dict()}")
        
        return df
    
    def _extract_pdf_urls(self, html_content):
        """Extract PDF URLs from page."""
        soup = BeautifulSoup(html_content, 'html.parser')
        pdf_urls = {}
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '.pdf' in href.lower():
                # Make absolute URL
                if href.startswith('/'):
                    pdf_url = 'https://www.fincen.gov' + href
                elif not href.startswith('http'):
                    pdf_url = 'https://www.fincen.gov/' + href
                else:
                    pdf_url = href
                
                # Categorize by keywords
                if 'southwest' in href.lower() or 'southern' in href.lower() or 'border' in href.lower():
                    pdf_urls['Southwest Border'] = pdf_url
                    logger.debug(f"  Found SW Border PDF: {pdf_url}")
        
        return pdf_urls
    
    def _get_sw_border_data(self, pdf_urls):
        """
        Get Southwest Border data with tier information.
        
        Returns:
            Dict with 'AZ' and 'TX' keys mapping county names to tiers
        """
        # Try to parse PDF if URL found
        if 'Southwest Border' in pdf_urls:
            try:
                pdf_url = pdf_urls['Southwest Border']
                logger.info(f"Parsing PDF: {pdf_url}")
                
                response = fetch_url(pdf_url, timeout=60)
                
                # Try pdfplumber
                try:
                    import pdfplumber
                    
                    with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                        text = "\n".join(page.extract_text() for page in pdf.pages)
                    
                    logger.debug(f"  Extracted {len(text)} chars from PDF")
                    parsed_data = self._parse_sw_border_text(text)
                    
                    if parsed_data['TX'] or parsed_data['AZ']:
                        logger.info("  ✓ Successfully parsed PDF")
                        return parsed_data
                
                except ImportError:
                    logger.warning("  pdfplumber not installed, using fallback data")
                
            except Exception as e:
                logger.warning(f"  Failed to parse PDF: {str(e)}, using fallback")
        
        # Fallback to known data
        logger.info("  Using fallback Southwest Border data")
        return self._get_sw_border_fallback()
    
    def _parse_sw_border_text(self, text):
        """Parse PDF text for Southwest Border counties."""
        import re
        
        result = {'AZ': {}, 'TX': {}}
        lines = text.split('\n')
        
        current_tier = None
        current_state = None
        
        for line in lines:
            line_lower = line.lower()
            
            # Detect tier
            if 'tier i' in line_lower or 'tier 1' in line_lower:
                current_tier = 'Tier I'
            elif 'tier ii' in line_lower or 'tier 2' in line_lower:
                current_tier = 'Tier II'
            
            # Detect state
            if 'texas' in line_lower:
                current_state = 'TX'
            elif 'arizona' in line_lower:
                current_state = 'AZ'
            
            # Extract counties
            match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+County', line)
            if match and current_tier and current_state:
                county_name = match.group(1)
                result[current_state][county_name] = current_tier
        
        return result if (result['TX'] or result['AZ']) else self._get_sw_border_fallback()
    
    def _get_sw_border_fallback(self):
        """Fallback Southwest Border data."""
        return {
            'AZ': {
                'Cochise': 'Tier I', 'Pima': 'Tier I', 'Santa Cruz': 'Tier I', 'Yuma': 'Tier I',
                'Apache': 'State-wide', 'Coconino': 'State-wide', 'Gila': 'State-wide',
                'Graham': 'State-wide', 'Greenlee': 'State-wide', 'La Paz': 'State-wide',
                'Maricopa': 'State-wide', 'Mohave': 'State-wide', 'Navajo': 'State-wide',
                'Pinal': 'State-wide', 'Yavapai': 'State-wide'
            },
            'TX': {
                'Cameron': 'Tier I', 'Hidalgo': 'Tier I', 'Starr': 'Tier I', 'Zapata': 'Tier I',
                'Webb': 'Tier I', 'Maverick': 'Tier I', 'Val Verde': 'Tier I', 'Terrell': 'Tier I',
                'Brewster': 'Tier I', 'Presidio': 'Tier I', 'Jeff Davis': 'Tier I',
                'Hudspeth': 'Tier I', 'El Paso': 'Tier I',
                'Willacy': 'Tier II', 'Jim Hogg': 'Tier II', 'Dimmit': 'Tier II', 'La Salle': 'Tier II',
                'Kinney': 'Tier II', 'Uvalde': 'Tier II', 'Edwards': 'Tier II', 'Crockett': 'Tier II',
                'Pecos': 'Tier II', 'Reeves': 'Tier II', 'Culberson': 'Tier II'
            }
        }
    
    def _get_california_counties(self):
        """Get California district counties."""
        ca_north = ['Monterey', 'Humboldt', 'Mendocino', 'Lake', 'Sonoma', 'Napa',
                    'Marin', 'Contra Costa', 'San Francisco', 'San Mateo', 'Alameda',
                    'Santa Cruz', 'San Benito', 'Del Norte']
        ca_south = ['Los Angeles', 'Orange', 'Riverside', 'San Bernardino',
                    'San Luis Obispo', 'Santa Barbara', 'Ventura']
        
        counties = []
        ca_all = fetch_census_counties('CA')
        
        for c in ca_all:
            if c['county_name'] in ca_north:
                counties.append(create_county_dict(
                    c, tier='Northern District', source_url=self.SOURCE_URL
                ))
            elif c['county_name'] in ca_south:
                counties.append(create_county_dict(
                    c, tier='Southern District', source_url=self.SOURCE_URL
                ))
        
        logger.debug(f"  CA: {len(counties)} counties")
        return counties
    
    def _get_other_regions(self):
        """Get other HIFCA region counties."""
        counties = []
        
        # Chicago
        chicago = ['Cook', 'McHenry', 'DuPage', 'Lake', 'Will', 'Kane']
        for c in fetch_census_counties('IL'):
            if c['county_name'] in chicago:
                counties.append(create_county_dict(c, source_url=self.SOURCE_URL))
        
        # New York (ALL)
        for c in fetch_census_counties('NY'):
            counties.append(create_county_dict(c, source_url=self.SOURCE_URL))
        
        # New Jersey (ALL)
        for c in fetch_census_counties('NJ'):
            counties.append(create_county_dict(c, source_url=self.SOURCE_URL))
        
        # Puerto Rico (ALL)
        for c in fetch_census_counties('PR'):
            counties.append(create_county_dict(c, source_url=self.SOURCE_URL))
        
        # Virgin Islands (ALL)
        for c in fetch_census_counties('VI'):
            counties.append(create_county_dict(c, source_url=self.SOURCE_URL))
        
        # South Florida
        south_fl = ['Broward', 'Miami-Dade', 'Indian River', 'Martin',
                    'Monroe', 'Okeechobee', 'Palm Beach', 'St. Lucie']
        for c in fetch_census_counties('FL'):
            if c['county_name'] in south_fl:
                counties.append(create_county_dict(c, source_url=self.SOURCE_URL))
        
        logger.debug(f"  Other regions: {len(counties)} counties")
        return counties
