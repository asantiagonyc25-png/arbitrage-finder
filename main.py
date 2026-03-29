"""Main orchestrator for the arbitrage finder."""

import logging
from typing import List, Dict, Optional
import time
import json
from datetime import datetime

from ebay_scraper import EbayScraper
from demand_validator import DemandValidator
from source_marketplace_finder import SourceMarketplaceFinder
from shipping_calculator import ShippingCalculator
from profit_calculator import ProfitCalculator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArbitrageFinder:
    """Main orchestrator for finding profitable arbitrage opportunities."""

    def __init__(self):
        self.ebay_scraper = EbayScraper()
        self.demand_validator = DemandValidator()
        self.marketplace_finder = SourceMarketplaceFinder()
        self.shipping_calculator = ShippingCalculator()
        self.profit_calculator = ProfitCalculator()
        self.results = []

    def analyze_product(self, product_name: str, verbose: bool = False) -> Optional[Dict]:
        """Analyze a single product for arbitrage opportunity.
        
        Args:
            product_name: Product to analyze
            verbose: Print detailed progress
            
        Returns:
            Analysis result or None if not viable
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Analyzing: {product_name}")
        logger.info(f"{'='*60}")

        # Step 1: Get eBay data
        logger.info("Step 1: Getting eBay data...")
        ebay_data = self.ebay_scraper.get_product_data(product_name)
        if not ebay_data:
            logger.warning(f"Could not get eBay data for {product_name}")
            return None

        logger.info(f"  Sold listings: {ebay_data['sold_listings']}")
        logger.info(f"  Active listings: {ebay_data['active_listings']}")
        logger.info(f"  Average price: ${ebay_data['avg_price']:.2f}")
        logger.info(f"  Sold/Active ratio: {ebay_data['sold_to_active_ratio']:.2f}")

        # Step 2: Validate demand
        logger.info("\nStep 2: Validating demand...")
        demand_analysis = self.demand_validator.validate_product(
            product_name,
            ebay_data['sold_listings'],
            ebay_data['active_listings'],
            ebay_data['avg_price']
        )

        logger.info(f"  Google Trends score: {demand_analysis['google_trend_score']}")
        logger.info(f"  Overall demand score: {demand_analysis['overall_demand_score']:.1f}/100")
        logger.info(f"  In demand: {demand_analysis['is_in_demand']}")

        # Skip if not in demand
        if not demand_analysis['is_in_demand']:
            logger.warning("Product does not meet demand criteria")
            return None

        # Step 3: Find source marketplaces
        logger.info("\nStep 3: Searching source marketplaces...")
        source_results = self.marketplace_finder.search_all(product_name, ebay_data['avg_price'])

        if not source_results:
            logger.warning("Could not find product on source marketplaces")
            return None

        logger.info(f"  Found on {len(source_results)} platforms")
        for source in source_results:
            logger.info(f"    {source['platform']}: ${source['min_price_usd']:.2f}")

        # Step 4: Analyze each source option
        logger.info("\nStep 4: Calculating profit for each source...")
        viable_opportunities = []

        for source_data in source_results:
            # Calculate shipping and landed cost
            shipping_info = self.shipping_calculator.calculate_total_cost(source_data)

            if not shipping_info:
                logger.debug(f"  Skipping {source_data['platform']} - could not calculate shipping")
                continue

            landed_cost = shipping_info.get('total_cost_usd', 999)
            ebay_price = ebay_data['avg_price']

            # Check if profitable
            if landed_cost >= ebay_price:
                logger.debug(f"  {source_data['platform']}: Cost too high (${landed_cost:.2f} vs ${ebay_price:.2f})")
                continue

            # Calculate profit
            opportunity = self.profit_calculator.evaluate_opportunity(
                product_name,
                ebay_price,
                demand_analysis['overall_demand_score'],
                source_data['platform'],
                source_data.get('min_price_usd', 0),
                shipping_info,
                quantity=1
            )

            if opportunity['is_winner']:
                logger.info(f"  ✓ WINNER: {source_data['platform']}")
                logger.info(f"    Profit per unit: ${opportunity['profit_per_unit']:.2f}")
                logger.info(f"    Profit margin: {opportunity['profit_margin_percent']:.1f}%")
                viable_opportunities.append(opportunity)
            else:
                logger.debug(f"  ✗ Not profitable enough: {source_data['platform']}")

        if not viable_opportunities:
            logger.warning("No profitable sources found for this product")
            return None

        # Return the best opportunity for this product
        best = sorted(viable_opportunities, key=lambda x: x['overall_score'], reverse=True)[0]
        return best

    def analyze_products(
        self,
        product_list: List[str],
        parallel: bool = False
    ) -> List[Dict]:
        """Analyze multiple products and return winners.
        
        Args:
            product_list: List of product names to analyze
            parallel: Whether to process in parallel (not implemented yet)
            
        Returns:
            List of winning opportunities
        """
        logger.info(f"Starting analysis of {len(product_list)} products...")
        logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        winners = []

        for product in product_list:
            try:
                result = self.analyze_product(product, verbose=False)
                if result:
                    winners.append(result)
                    self.results.append(result)

                # Rate limiting
                time.sleep(2)

            except Exception as e:
                logger.error(f"Error analyzing {product}: {e}")
                continue

        # Sort winners by overall score
        winners = sorted(winners, key=lambda x: x['overall_score'], reverse=True)

        return winners

    def print_results(self, winners: List[Dict]):
        """Print results in a clean format."""
        logger.info(f"\n{'='*80}")
        logger.info("🎯 ARBITRAGE OPPORTUNITY WINNERS 🎯")
        logger.info(f"{'='*80}")

        if not winners:
            logger.info("No winning products found.")
            return

        logger.info(f"\nFound {len(winners)} winning products!\n")

        for i, winner in enumerate(winners, 1):
            logger.info(f"{i}. {winner['product_name']}")
            logger.info(f"   Source: {winner['source_platform']}")
            logger.info(f"   eBay Selling Price: ${winner['ebay_selling_price']:.2f}")
            logger.info(f"   Landed Cost: ${winner['landed_cost']:.2f}")
            logger.info(f"   Profit per unit: ${winner['profit_per_unit']:.2f}")
            logger.info(f"   Profit margin: {winner['profit_margin_percent']:.1f}%")
            logger.info(f"   Demand score: {winner['ebay_demand_score']:.1f}/100")
            logger.info(f"   Overall score: {winner['overall_score']:.1f}")
            logger.info()

        logger.info(f"{'='*80}")
        logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*80}")

    def save_results(self, filename: str = "results.json"):
        """Save results to JSON file."""
        with open(filename, 'w') as f:
            # Convert decimals to strings for JSON serialization
            serializable_results = self._make_serializable(self.results)
            json.dump(serializable_results, f, indent=2)
        logger.info(f"Results saved to {filename}")

    def _make_serializable(self, obj):
        """Convert objects to JSON-serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (int, str, bool, type(None))):
            return obj
        elif isinstance(obj, float):
            return round(obj, 2)
        else:
            return str(obj)

    def run_analysis(self, products: List[str]):
        """Run complete analysis and display results."""
        winners = self.analyze_products(products)
        self.print_results(winners)
        self.save_results()


if __name__ == "__main__":
    import sys

    # Default products to analyze
    default_products = [
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

    # Allow passing products from command line
    if len(sys.argv) > 1:
        products = sys.argv[1:]
    else:
        products = default_products

    finder = ArbitrageFinder()
    finder.run_analysis(products)
