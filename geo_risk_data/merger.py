"""
Merge HIFCA and HIDTA datasets
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def merge_datasets(hifca_df, hidta_df):
    """
    Merge HIFCA and HIDTA datasets with designation flags.
    
    Args:
        hifca_df: DataFrame with HIFCA data
        hidta_df: DataFrame with HIDTA data
        
    Returns:
        DataFrame with merged data and flags
    """
    logger.info("Merging HIFCA and HIDTA datasets...")
    
    # Add flags
    hifca_df = hifca_df.copy()
    hidta_df = hidta_df.copy()
    
    hifca_df['hifca_flag'] = 1
    hidta_df['hidta_flag'] = 1
    
    # Merge on county_fips - full outer join
    merged = pd.merge(
        hifca_df,
        hidta_df,
        on='county_fips',
        how='outer',
        suffixes=('', '_hidta')
    )
    
    # Fill in missing state info from either side
    if 'state_id_hidta' in merged.columns:
        merged['state_id'] = merged['state_id'].fillna(merged['state_id_hidta'])
        merged['state_name'] = merged['state_name'].fillna(merged['state_name_hidta'])
        merged['county_name'] = merged['county_name'].fillna(merged['county_name_hidta'])
        
        # Drop duplicate columns
        cols_to_drop = [col for col in merged.columns if col.endswith('_hidta')]
        merged = merged.drop(columns=cols_to_drop)
    
    # Fill in last_extracted_date from either side
    if 'last_extracted_date_hidta' in merged.columns:
        merged['last_extracted_date'] = merged['last_extracted_date'].fillna(
            merged['last_extracted_date_hidta']
        )
    
    # Fill NaN flags
    merged['hifca_flag'] = merged['hifca_flag'].fillna(0).astype(int)
    merged['hidta_flag'] = merged['hidta_flag'].fillna(0).astype(int)
    
    # Create combined flag
    merged['hifca_hidta_flag'] = merged.apply(
        lambda row: 'BOTH' if (row['hifca_flag'] == 1 and row['hidta_flag'] == 1)
                    else 'HIFCA' if row['hifca_flag'] == 1
                    else 'HIDTA' if row['hidta_flag'] == 1
                    else 'NONE',
        axis=1
    )
    
    # Combine source URLs
    if 'source_url' in merged.columns:
        merged['source_url'] = merged.apply(
            lambda row: row.get('source_url', '') if pd.notna(row.get('source_url'))
                        else row.get('source_url_hidta', '') if pd.notna(row.get('source_url_hidta'))
                        else '',
            axis=1
        )
    
    # Reorder columns
    base_cols = ['state_id', 'state_name', 'county_fips', 'county_name']
    flag_cols = ['hifca_flag', 'hidta_flag', 'hifca_hidta_flag']
    tier_cols = ['hifca_tier'] if 'hifca_tier' in merged.columns else []
    meta_cols = ['source_url', 'last_extracted_date']
    
    column_order = base_cols + flag_cols + tier_cols + meta_cols
    column_order = [col for col in column_order if col in merged.columns]
    
    # Add any remaining columns
    remaining_cols = [col for col in merged.columns if col not in column_order]
    column_order.extend(remaining_cols)
    
    merged = merged[column_order]
    
    # Sort
    merged = merged.sort_values(['state_id', 'county_name']).reset_index(drop=True)
    
    # Log summary
    logger.info(f"✓ Merge complete: {len(merged)} total counties")
    logger.info(f"  HIFCA only: {len(merged[merged['hifca_hidta_flag'] == 'HIFCA'])}")
    logger.info(f"  HIDTA only: {len(merged[merged['hifca_hidta_flag'] == 'HIDTA'])}")
    logger.info(f"  Both: {len(merged[merged['hifca_hidta_flag'] == 'BOTH'])}")
    
    return merged
