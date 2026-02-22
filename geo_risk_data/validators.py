"""
Layout validation and change detection for source pages
"""

import json
import hashlib
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when data validation fails"""
    pass


class LayoutChangedError(Exception):
    """Raised when source page layout has changed significantly"""
    pass


class LayoutValidator:
    """
    Validates and compares webpage layouts to detect significant changes.
    """
    
    def __init__(self, cache_dir):
        """
        Initialize layout validator.
        
        Args:
            cache_dir: Directory to store layout snapshots
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_layout_signature(self, html_content, url):
        """
        Extract layout signature from HTML content.
        
        Args:
            html_content: HTML string
            url: Source URL
            
        Returns:
            Dict with layout information
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        signature = {
            'url': url,
            'extraction_date': datetime.now().isoformat(),
            'content_hash': hashlib.sha256(html_content.encode()).hexdigest(),
            'structure': {
                'table_count': len(soup.find_all('table')),
                'div_count': len(soup.find_all('div')),
                'link_count': len(soup.find_all('a')),
                'pdf_links': [],
                'table_structures': [],
            }
        }
        
        # Extract PDF links
        for link in soup.find_all('a', href=True):
            if '.pdf' in link['href'].lower():
                signature['structure']['pdf_links'].append({
                    'href': link['href'],
                    'text': link.get_text(strip=True)
                })
        
        # Extract table structures
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            table_info = {
                'row_count': len(rows),
                'header_cells': len(rows[0].find_all(['th', 'td'])) if rows else 0,
            }
            signature['structure']['table_structures'].append(table_info)
        
        return signature
    
    def get_snapshot_path(self, url):
        """
        Get path for layout snapshot file.
        
        Args:
            url: Source URL
            
        Returns:
            Path object
        """
        # Create filename from URL
        url_hash = hashlib.md5(url.encode()).hexdigest()[:16]
        filename = f"layout_{url_hash}.json"
        return self.cache_dir / filename
    
    def save_snapshot(self, signature):
        """
        Save layout snapshot to cache.
        
        Args:
            signature: Layout signature dict
        """
        snapshot_path = self.get_snapshot_path(signature['url'])
        
        with open(snapshot_path, 'w') as f:
            json.dump(signature, f, indent=2)
        
        logger.debug(f"Saved layout snapshot: {snapshot_path}")
    
    def load_snapshot(self, url):
        """
        Load previous layout snapshot from cache.
        
        Args:
            url: Source URL
            
        Returns:
            Dict with layout signature or None if not found
        """
        snapshot_path = self.get_snapshot_path(url)
        
        if not snapshot_path.exists():
            logger.debug(f"No previous snapshot found for {url}")
            return None
        
        try:
            with open(snapshot_path, 'r') as f:
                snapshot = json.load(f)
            logger.debug(f"Loaded layout snapshot from {snapshot['extraction_date']}")
            return snapshot
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to load snapshot: {str(e)}")
            return None
    
    def compare_layouts(self, old_signature, new_signature):
        """
        Compare two layout signatures and detect significant changes.
        
        Args:
            old_signature: Previous layout signature
            new_signature: Current layout signature
            
        Returns:
            Dict with comparison results and list of changes
        """
        changes = []
        
        # Compare content hash (exact content match)
        if old_signature['content_hash'] == new_signature['content_hash']:
            return {'changed': False, 'changes': []}
        
        old_struct = old_signature['structure']
        new_struct = new_signature['structure']
        
        # Compare table count
        if old_struct['table_count'] != new_struct['table_count']:
            changes.append({
                'type': 'TABLE_COUNT_CHANGED',
                'severity': 'HIGH',
                'old': old_struct['table_count'],
                'new': new_struct['table_count']
            })
        
        # Compare table structures
        if len(old_struct['table_structures']) == len(new_struct['table_structures']):
            for i, (old_table, new_table) in enumerate(zip(
                old_struct['table_structures'],
                new_struct['table_structures']
            )):
                if old_table['row_count'] != new_table['row_count']:
                    changes.append({
                        'type': 'TABLE_ROWS_CHANGED',
                        'severity': 'MEDIUM',
                        'table_index': i,
                        'old': old_table['row_count'],
                        'new': new_table['row_count']
                    })
                
                if old_table['header_cells'] != new_table['header_cells']:
                    changes.append({
                        'type': 'TABLE_COLUMNS_CHANGED',
                        'severity': 'HIGH',
                        'table_index': i,
                        'old': old_table['header_cells'],
                        'new': new_table['header_cells']
                    })
        
        # Compare PDF links
        old_pdfs = set(pdf['href'] for pdf in old_struct['pdf_links'])
        new_pdfs = set(pdf['href'] for pdf in new_struct['pdf_links'])
        
        removed_pdfs = old_pdfs - new_pdfs
        added_pdfs = new_pdfs - old_pdfs
        
        if removed_pdfs:
            changes.append({
                'type': 'PDF_LINKS_REMOVED',
                'severity': 'MEDIUM',
                'removed': list(removed_pdfs)
            })
        
        if added_pdfs:
            changes.append({
                'type': 'PDF_LINKS_ADDED',
                'severity': 'LOW',
                'added': list(added_pdfs)
            })
        
        return {
            'changed': len(changes) > 0,
            'changes': changes,
            'high_severity_count': len([c for c in changes if c['severity'] == 'HIGH']),
            'medium_severity_count': len([c for c in changes if c['severity'] == 'MEDIUM']),
        }
    
    def validate_layout(self, html_content, url, fail_on_change=True):
        """
        Validate page layout and detect significant changes.
        
        Args:
            html_content: HTML string
            url: Source URL
            fail_on_change: If True, raise exception on significant changes
            
        Returns:
            Tuple of (is_valid, changes_dict)
            
        Raises:
            LayoutChangedError: If layout has changed significantly and fail_on_change=True
        """
        # Extract current signature
        new_signature = self.extract_layout_signature(html_content, url)
        
        # Load previous snapshot
        old_signature = self.load_snapshot(url)
        
        if old_signature is None:
            # No previous snapshot - save this as baseline
            logger.info(f"No previous layout found - saving baseline for {url}")
            self.save_snapshot(new_signature)
            return True, {'changed': False, 'is_baseline': True}
        
        # Compare layouts
        comparison = self.compare_layouts(old_signature, new_signature)
        
        if comparison['changed']:
            logger.warning(f"Layout changes detected for {url}")
            logger.warning(f"  High severity: {comparison['high_severity_count']}")
            logger.warning(f"  Medium severity: {comparison['medium_severity_count']}")
            
            for change in comparison['changes']:
                logger.warning(f"  - {change['type']}: {change.get('old')} → {change.get('new')}")
            
            # Update snapshot with new layout
            self.save_snapshot(new_signature)
            
            if fail_on_change and comparison['high_severity_count'] > 0:
                raise LayoutChangedError(
                    f"Significant layout changes detected on {url}. "
                    f"Found {comparison['high_severity_count']} high-severity changes. "
                    f"Review changes and update scraping logic if needed."
                )
        else:
            logger.debug(f"Layout unchanged for {url}")
        
        return not comparison['changed'], comparison


def validate_county_data(df, min_counties=10, expected_columns=None):
    """
    Validate extracted county data.
    
    Args:
        df: pandas DataFrame with county data
        min_counties: Minimum expected county count
        expected_columns: List of expected column names
        
    Raises:
        ValidationError: If validation fails
    """
    if expected_columns is None:
        expected_columns = ['state_id', 'state_name', 'county_fips', 'county_name']
    
    # Check DataFrame is not empty
    if len(df) == 0:
        raise ValidationError("Extracted data is empty")
    
    # Check minimum county count
    if len(df) < min_counties:
        raise ValidationError(
            f"Extracted only {len(df)} counties, expected at least {min_counties}"
        )
    
    # Check required columns exist
    missing_cols = set(expected_columns) - set(df.columns)
    if missing_cols:
        raise ValidationError(f"Missing required columns: {missing_cols}")
    
    # Check for null values in key columns
    for col in ['state_id', 'county_fips', 'county_name']:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                raise ValidationError(f"Found {null_count} null values in {col}")
    
    # Check FIPS codes are valid format (5 digits)
    if 'county_fips' in df.columns:
        invalid_fips = df[~df['county_fips'].str.match(r'^\d{5}$', na=False)]
        if len(invalid_fips) > 0:
            raise ValidationError(
                f"Found {len(invalid_fips)} invalid FIPS codes: "
                f"{invalid_fips['county_fips'].head().tolist()}"
            )
    
    logger.info(f"✓ Data validation passed: {len(df)} counties")
