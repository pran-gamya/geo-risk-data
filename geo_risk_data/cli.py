"""
Command-line interface for geo-risk-data
"""

def main():
    parser = argparse.ArgumentParser(...)
    
    # Make mode optional instead of required
    mode_group = parser.add_mutually_exclusive_group(required=False)  # Changed to False
    mode_group.add_argument('--hifca', ...)
    mode_group.add_argument('--hidta', ...)
    mode_group.add_argument('--both', ...)
    
    parser.add_argument('--output', '-o', type=str, required=False)  # Changed to False
    
    args = parser.parse_args()
    
    # If no mode specified, run interactive
    if not any([args.hifca, args.hidta, args.both]):
        return interactive_mode()

import argparse
import sys
import logging
from pathlib import Path

from . import get_hifca, get_hidta, get_combined, __version__
from .utils import setup_logging
from .validators import LayoutChangedError, ValidationError


def main():
    """Main CLI entry point."""
    
    parser = argparse.ArgumentParser(
        description='Extract HIFCA and HIDTA county-level geographic risk data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get HIFCA data only
  geo-risk-data --hifca --output hifca_counties.csv
  
  # Get HIDTA data only
  geo-risk-data --hidta --output hidta_counties.csv
  
  # Get combined data (default)
  geo-risk-data --both --output combined.csv
  
  # Skip layout validation (faster but less safe)
  geo-risk-data --both --no-validate --output combined.csv
  
  # Verbose logging
  geo-risk-data --both --verbose --output combined.csv
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'geo-risk-data {__version__}'
    )
    
    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--hifca',
        action='store_true',
        help='Extract HIFCA data only'
    )
    mode_group.add_argument(
        '--hidta',
        action='store_true',
        help='Extract HIDTA data only'
    )
    mode_group.add_argument(
        '--both',
        action='store_true',
        help='Extract and merge both HIFCA and HIDTA data (default)'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        type=str,
        required=True,
        help='Output CSV file path'
    )
    
    # Validation options
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip layout validation (faster but may fail if source pages changed)'
    )
    
    parser.add_argument(
        '--cache-dir',
        type=str,
        help='Cache directory for layout snapshots (default: ~/.geo_risk_data/cache)'
    )
    
    # Logging options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress all output except errors'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    # Determine mode
    validate_layout = not args.no_validate
    
    try:
        logger.info("=" * 70)
        logger.info("GEO-RISK-DATA EXTRACTOR")
        logger.info("=" * 70)
        
        # Execute based on mode
        if args.hifca:
            logger.info("Mode: HIFCA only")
            df = get_hifca(validate_layout=validate_layout, cache_dir=args.cache_dir)
        
        elif args.hidta:
            logger.info("Mode: HIDTA only")
            df = get_hidta(validate_layout=validate_layout, cache_dir=args.cache_dir)
        
        elif args.both:
            logger.info("Mode: Combined HIFCA + HIDTA")
            df = get_combined(validate_layout=validate_layout, cache_dir=args.cache_dir)
        
        # Save output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_path, index=False)
        
        logger.info("=" * 70)
        logger.info(f"✓ SUCCESS: Saved {len(df)} counties to {output_path}")
        logger.info("=" * 70)
        
        # Print summary
        if not args.quiet:
            print(f"\n✓ Extracted {len(df)} counties")
            print(f"✓ Saved to: {output_path}")
            
            if args.both and 'hifca_hidta_flag' in df.columns:
                print(f"\nBreakdown:")
                print(df['hifca_hidta_flag'].value_counts().to_string())
        
        return 0
        
    except LayoutChangedError as e:
        logger.error("=" * 70)
        logger.error("LAYOUT CHANGED ERROR")
        logger.error("=" * 70)
        logger.error(str(e))
        logger.error("")
        logger.error("The source page layout has changed significantly.")
        logger.error("This may indicate the scraping logic needs updating.")
        logger.error("")
        logger.error("Options:")
        logger.error("  1. Review the changes and update the code if needed")
        logger.error("  2. Run with --no-validate to skip validation (not recommended)")
        logger.error("=" * 70)
        return 1
        
    except ValidationError as e:
        logger.error("=" * 70)
        logger.error("VALIDATION ERROR")
        logger.error("=" * 70)
        logger.error(str(e))
        logger.error("")
        logger.error("The extracted data failed validation.")
        logger.error("This may indicate incomplete or incorrect data extraction.")
        logger.error("=" * 70)
        return 1
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error("UNEXPECTED ERROR")
        logger.error("=" * 70)
        logger.error(str(e))
        
        if args.verbose:
            import traceback
            logger.error("\nTraceback:")
            logger.error(traceback.format_exc())
        
        logger.error("=" * 70)
        return 1


if __name__ == '__main__':
    sys.exit(main())
