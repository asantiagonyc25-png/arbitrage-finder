"""Utility functions for the arbitrage finder."""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ResultFormatter:
    """Formats analyzer results for different output types."""

    @staticmethod
    def format_as_table(winners: List[Dict]) -> str:
        """Format results as ASCII table."""
        if not winners:
            return "No winning products found.\n"

        # Header
        output = "\n" + "=" * 120 + "\n"
        output += "| " + "Product Name".ljust(20) + " | "
        output += " Source ".ljust(15) + " | "
        output += " eBay Price ".ljust(12) + " | "
        output += " Cost ".ljust(10) + " | "
        output += " Profit ".ljust(10) + " | "
        output += " Margin % ".ljust(10) + " | "
        output += " Demand ".ljust(8) + " |\n"
        output += "=" * 120 + "\n"

        # Rows
        for winner in winners:
            product = winner['product_name'][:19]
            source = winner['source_platform'][:14]
            ebay_price = f"${winner['ebay_selling_price']:.0f}"
            cost = f"${winner['landed_cost']:.0f}"
            profit = f"${winner['profit_per_unit']:.0f}"
            margin = f"{winner['profit_margin_percent']:.1f}%"
            demand = f"{winner['ebay_demand_score']:.0f}/100"

            output += "| " + product.ljust(20) + " | "
            output += source.ljust(15) + " | "
            output += ebay_price.ljust(12) + " | "
            output += cost.ljust(10) + " | "
            output += profit.ljust(10) + " | "
            output += margin.ljust(10) + " | "
            output += demand.ljust(8) + " |\n"

        output += "=" * 120 + "\n"
        return output

    @staticmethod
    def format_as_csv(winners: List[Dict]) -> str:
        """Format results as CSV."""
        if not winners:
            return ""

        output = "Product Name,Source Platform,eBay Price,Landed Cost,Profit per Unit,Profit Margin %,Demand Score,Overall Score\n"

        for winner in winners:
            output += f"{winner['product_name']},{winner['source_platform']},"
            output += f"${winner['ebay_selling_price']:.2f},"
            output += f"${winner['landed_cost']:.2f},"
            output += f"${winner['profit_per_unit']:.2f},"
            output += f"{winner['profit_margin_percent']:.2f}%,"
            output += f"{winner['ebay_demand_score']:.1f},"
            output += f"{winner['overall_score']:.1f}\n"

        return output

    @staticmethod
    def format_as_markdown(winners: List[Dict]) -> str:
        """Format results as Markdown."""
        if not winners:
            return "No winning products found.\n"

        output = "# Arbitrage Opportunities\n\n"
        output += f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        output += f"**Total Winners Found**: {len(winners)}\n\n"

        output += "| Rank | Product | Source | eBay $ | Cost $ | Profit $ | Margin | Demand |\n"
        output += "|------|---------|--------|--------|--------|----------|--------|--------|\n"

        for i, winner in enumerate(winners, 1):
            output += f"| {i} | {winner['product_name']} | {winner['source_platform']} | "
            output += f"${winner['ebay_selling_price']:.0f} | ${winner['landed_cost']:.0f} | "
            output += f"${winner['profit_per_unit']:.0f} | {winner['profit_margin_percent']:.0f}% | "
            output += f"{winner['ebay_demand_score']:.0f}/100 |\n"

        output += "\n## Details\n\n"
        for i, winner in enumerate(winners, 1):
            output += f"### {i}. {winner['product_name']}\n\n"
            output += f"- **Source Platform**: {winner['source_platform']}\n"
            output += f"- **eBay Selling Price**: ${winner['ebay_selling_price']:.2f}\n"
            output += f"- **Landed Cost**: ${winner['landed_cost']:.2f}\n"
            output += f"- **Profit per Unit**: ${winner['profit_per_unit']:.2f}\n"
            output += f"- **Profit Margin**: {winner['profit_margin_percent']:.2f}%\n"
            output += f"- **Demand Score**: {winner['ebay_demand_score']:.1f}/100\n"
            output += f"- **Overall Score**: {winner['overall_score']:.1f}\n\n"

        return output


class PriceFormatter:
    """Utilities for price formatting and currency conversion."""

    @staticmethod
    def usd_to_cny(usd: float) -> float:
        """Convert USD to Chinese Yuan (approximate)."""
        return usd * 7.0

    @staticmethod
    def cny_to_usd(cny: float) -> float:
        """Convert Chinese Yuan to USD (approximate)."""
        return cny / 7.0

    @staticmethod
    def usd_to_jpy(usd: float) -> float:
        """Convert USD to Japanese Yen (approximate)."""
        return usd * 150

    @staticmethod
    def jpy_to_usd(jpy: float) -> float:
        """Convert Japanese Yen to USD (approximate)."""
        return jpy / 150

    @staticmethod
    def format_price(price: float, currency: str = "USD") -> str:
        """Format price with currency symbol."""
        if currency == "USD":
            return f"${price:.2f}"
        elif currency == "CNY":
            return f"¥{price:.0f}"
        elif currency == "JPY":
            return f"¥{price:.0f}"
        return f"{price:.2f} {currency}"


class AnalysisStats:
    """Generate statistics from analysis results."""

    @staticmethod
    def calculate_stats(winners: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics from winners."""
        if not winners:
            return {}

        profits = [w['profit_per_unit'] for w in winners]
        margins = [w['profit_margin_percent'] for w in winners]
        demands = [w['ebay_demand_score'] for w in winners]

        return {
            'total_winners': len(winners),
            'avg_profit_per_unit': sum(profits) / len(profits),
            'avg_profit_margin': sum(margins) / len(margins),
            'avg_demand_score': sum(demands) / len(demands),
            'highest_profit': max(profits),
            'highest_margin': max(margins),
            'platform_breakdown': AnalysisStats._platform_breakdown(winners),
        }

    @staticmethod
    def _platform_breakdown(winners: List[Dict]) -> Dict[str, int]:
        """Count winners by source platform."""
        breakdown = {}
        for winner in winners:
            platform = winner['source_platform']
            breakdown[platform] = breakdown.get(platform, 0) + 1
        return breakdown

    @staticmethod
    def print_stats(stats: Dict):
        """Print statistics in readable format."""
        if not stats:
            print("No statistics available.")
            return

        print("\n" + "=" * 60)
        print("📊 ANALYSIS STATISTICS")
        print("=" * 60)
        print(f"Total Winners Found: {stats['total_winners']}")
        print(f"Average Profit per Unit: ${stats['avg_profit_per_unit']:.2f}")
        print(f"Average Profit Margin: {stats['avg_profit_margin']:.1f}%")
        print(f"Average Demand Score: {stats['avg_demand_score']:.1f}/100")
        print(f"Highest Profit: ${stats['highest_profit']:.2f}")
        print(f"Highest Margin: {stats['highest_margin']:.1f}%")
        print("\nBy Platform:")
        for platform, count in stats['platform_breakdown'].items():
            print(f"  {platform}: {count} products")
        print("=" * 60 + "\n")


def setup_logging(log_level=logging.INFO, log_file=None):
    """Setup logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if log_file:
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(
            level=log_level,
            format=log_format
        )


def save_json(data: Any, filename: str):
    """Save data to JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    logger.info(f"Data saved to {filename}")


def load_json(filename: str) -> Any:
    """Load data from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)
