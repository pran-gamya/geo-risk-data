"""
Tests for geo-risk-data package
"""

import pytest
import pandas as pd
from geo_risk_data import get_hifca, get_hidta, get_combined
from geo_risk_data.validators import ValidationError, LayoutChangedError


class TestHIFCA:
    """Tests for HIFCA extraction"""
    
    def test_hifca_extraction(self):
        """Test basic HIFCA extraction"""
        df = get_hifca(validate_layout=False)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 200, "Should have at least 200 HIFCA counties"
        assert 'state_id' in df.columns
        assert 'county_fips' in df.columns
        assert 'county_name' in df.columns
        assert 'source_url' in df.columns
        assert 'last_extracted_date' in df.columns
    
    def test_hifca_tier_information(self):
        """Test that tier information is included"""
        df = get_hifca(validate_layout=False)
        
        assert 'hifca_tier' in df.columns
        
        # Should have Tier I counties
        tier1 = df[df['hifca_tier'] == 'Tier I']
        assert len(tier1) > 0, "Should have Tier I counties"
        
        # Should have Tier II counties
        tier2 = df[df['hifca_tier'] == 'Tier II']
        assert len(tier2) > 0, "Should have Tier II counties"
    
    def test_hifca_fips_codes(self):
        """Test FIPS codes are valid"""
        df = get_hifca(validate_layout=False)
        
        # All FIPS should be 5 digits
        assert df['county_fips'].str.match(r'^\d{5}$').all()
        
        # No null values
        assert df['county_fips'].notna().all()


class TestHIDTA:
    """Tests for HIDTA extraction"""
    
    def test_hidta_extraction(self):
        """Test basic HIDTA extraction"""
        df = get_hidta(validate_layout=False)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 600, "Should have at least 600 HIDTA counties"
        assert 'state_id' in df.columns
        assert 'county_fips' in df.columns
        assert 'source_url' in df.columns
        assert 'last_extracted_date' in df.columns
    
    def test_hidta_regions(self):
        """Test that multiple HIDTA regions are included"""
        df = get_hidta(validate_layout=False)
        
        # Should have multiple states
        assert df['state_id'].nunique() > 20, "Should have counties from 20+ states"
    
    def test_hidta_fips_codes(self):
        """Test FIPS codes are valid"""
        df = get_hidta(validate_layout=False)
        
        # All FIPS should be 5 digits
        assert df['county_fips'].str.match(r'^\d{5}$').all()


class TestCombined:
    """Tests for combined HIFCA+HIDTA"""
    
    def test_combined_extraction(self):
        """Test combined extraction"""
        df = get_combined(validate_layout=False)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 800, "Should have at least 800 total counties"
        
        # Should have flags
        assert 'hifca_flag' in df.columns
        assert 'hidta_flag' in df.columns
        assert 'hifca_hidta_flag' in df.columns
    
    def test_combined_flags(self):
        """Test designation flags"""
        df = get_combined(validate_layout=False)
        
        # Check flag values
        assert set(df['hifca_flag'].unique()) == {0, 1}
        assert set(df['hidta_flag'].unique()) == {0, 1}
        assert set(df['hifca_hidta_flag'].unique()).issubset({'HIFCA', 'HIDTA', 'BOTH'})
        
        # Should have some overlap
        both = df[df['hifca_hidta_flag'] == 'BOTH']
        assert len(both) > 0, "Should have counties in both HIFCA and HIDTA"
        
        # BOTH should mean both flags are 1
        assert (both['hifca_flag'] == 1).all()
        assert (both['hidta_flag'] == 1).all()
    
    def test_combined_tier_preserved(self):
        """Test that HIFCA tier information is preserved"""
        df = get_combined(validate_layout=False)
        
        assert 'hifca_tier' in df.columns
        
        # HIFCA counties should have tier info
        hifca_counties = df[df['hifca_flag'] == 1]
        tier_info = hifca_counties['hifca_tier'].notna()
        
        # At least some should have tier info
        assert tier_info.sum() > 0, "HIFCA counties should have tier information"


class TestDataQuality:
    """Tests for data quality"""
    
    def test_no_duplicate_fips(self):
        """Test no duplicate FIPS codes"""
        df = get_combined(validate_layout=False)
        
        duplicates = df[df.duplicated(subset=['county_fips'], keep=False)]
        assert len(duplicates) == 0, f"Found duplicate FIPS codes: {duplicates['county_fips'].unique()}"
    
    def test_state_codes_valid(self):
        """Test state codes are valid 2-letter codes"""
        df = get_combined(validate_layout=False)
        
        assert df['state_id'].str.match(r'^[A-Z]{2}$').all()
    
    def test_dates_present(self):
        """Test extraction dates are present"""
        df = get_combined(validate_layout=False)
        
        assert df['last_extracted_date'].notna().all()
        
        # Dates should be in YYYY-MM-DD format
        assert df['last_extracted_date'].str.match(r'^\d{4}-\d{2}-\d{2}$').all()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
