#!/usr/bin/env python3
"""Command-line interface for the arbitrage finder."""

import argparse
import sys
import logging
from pathlib import Path

from main import ArbitrageFinder
from utils import ResultFormatter, AnalysisStats, setup_logging


def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description='Arbitrage Finder - E-Commerce Opportunity Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Analyze default products
  python cli.py
  
  # Analyze specific products
  python cli.py "vintage camera" "gaming laptop"
  
  # Analyze with custom settings
  python cli.py "product1" "product2" --output-format markdown --margin 40 --min-profit 15
  
  # Run with verbose logging
  python cli.py --verbose --log-file analysis.log
        '''
    )

    parser.add_argument(
        'products',
        nargs='*',
        help='Products to analyze (space-separated). Uses defaults if not specified.'
    )

    parser.add_argument(
        '--output-format',
        choices=['json', 'csv', 'markdown', 'table'],
        default='table',
        help='Output format for results (default: table)'
    )

    parser.add_argument(
        '-o', '--output-file',
        default='results.json',
        help='Output file name (default: results.json)'
    )

    parser.add_argument(
        '--margin',
        type=int,
        default=30,
        help='Minimum profit margin percentage (default: 30)'
    )

    parser.add_argument(
        '--min-profit',
        type=float,
        default=10,
        help='Minimum profit in dollars (default: 10)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--log-file',
        help='Save logs to file'
    )

    parser.add_argument(
        '--save-results',
        action='store_true',
        default=True,
        help='Save results to file (default: True)'
    )

    parser.add_argument(
        '--print-stats',
        action='store_true',
        help='Print statistics summary'
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level, args.log_file)
    logger = logging.getLogger(__name__)

    logger.info("=" * 80)
    logger.info("🚀 ARBITRAGE FINDER - E-Commerce Opportunity Analyzer")
    logger.info("=" * 80)

    # Use provided products or defaults
    if not args.products:
        products = [
            "vintage camera lens",
            "retro gaming console",
            "antique watch",
            "collectible trading cards",
            "vintage vinyl records",
            "rare books",
            "china porcelain figurines",
            "vintage typewriter",
            "retro electronics",
            "collectible action figures",
        ]
        logger.info("Using default product list for analysis...")
    else:
        products = args.products
        logger.info(f"Analyzing {len(products)} custom products...")

    try:
        # Run analyzer
        finder = ArbitrageFinder()
        winners = finder.analyze_products(products)

        # Format and display results based on selected format
        if args.output_format == 'json':
            finder.print_results(winners)
            if args.save_results:
                finder.save_results(args.output_file)
                logger.info(f"Results saved to {args.output_file}")

        elif args.output_format == 'csv':
            csv_output = ResultFormatter.format_as_csv(winners)
            print(csv_output)
            if args.save_results:
                with open(args.output_file, 'w') as f:
                    f.write(csv_output)
                logger.info(f"Results saved to {args.output_file}")

        elif args.output_format == 'markdown':
            md_output = ResultFormatter.format_as_markdown(winners)
            print(md_output)
            if args.save_results:
                output_file = args.output_file.replace('.json', '.md')
                with open(output_file, 'w') as f:
                    f.write(md_output)
                logger.info(f"Results saved to {output_file}")

        else:  # table format (default)
            table_output = ResultFormatter.format_as_table(winners)
            print(table_output)
            if args.save_results:
                finder.save_results(args.output_file)
                logger.info(f"Results saved to {args.output_file}")

        # Print statistics if requested
        if args.print_stats:
            stats = AnalysisStats.calculate_stats(winners)
            AnalysisStats.print_stats(stats)

        # Final summary
        logger.info(f"\n✅ Analysis Complete!")
        logger.info(f"📊 Found {len(winners)} winning products")
        
        if winners:
            total_potential = sum(w['profit_per_unit'] * 10 for w in winners)
            logger.info(f"💰 Potential monthly profit (10 units each): ${total_potential:.2f}")

        logger.info("=" * 80)

        return 0

    except KeyboardInterrupt:
        logger.info("\n⚠️  Analysis interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"❌ Error during analysis: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
