"""Demand validation module with optional Google Trends support."""

import logging
from typing import Dict, Optional
import time

logger = logging.getLogger(__name__)


class DemandValidator:
    """Validates product demand using eBay metrics and optional Google Trends."""

    def __init__(self):
        self.request_count = 0
        self.pytrends = None
        self._init_pytrends()

    def _init_pytrends(self):
        """Safely initialize Google Trends support."""
        try:
            from pytrends.trends import TrendReq
            self.pytrends = TrendReq(hl='en-US', tz=360)
            logger.debug("Google Trends integration enabled")
        except ImportError:
            logger.debug("pytrends not installed - using heuristic scoring")
            self.pytrends = None
        except Exception as e:
            logger.debug(f"Could not initialize Google Trends: {e}")
            self.pytrends = None

    def get_google_trend_score(self, product_name: str, timeframe: str = "today 3m") -> Optional[int]:
        """Get Google Trends interest score for a product.
        
        Args:
            product_name: Product name to search
            timeframe: Timeframe for search (default: last 3 months)
            
        Returns:
            Interest score 0-100, or heuristic score if service unavailable
        """
        if not self.pytrends:
            # Return a heuristic score based on product name
            # Products with more specific descriptors tend to be more marketable
            base_score = 45
            word_count = len(product_name.split())
            keyword_boost = (word_count - 1) * 3  # More descriptive = slightly higher
            return min(100, base_score + keyword_boost)
        
        try:
            time.sleep(0.5)  # Rate limiting for Google
            self.pytrends.build_payload([product_name], timeframe=timeframe)
            interest_over_time = self.pytrends.interest_over_time()
            
            if interest_over_time.empty:
                logger.debug(f"No Google Trends data for {product_name}")
                return 50
            
            # Get the average interest over the period
            avg_interest = interest_over_time[product_name].mean()
            return max(0, min(100, int(avg_interest)))
            
        except Exception as e:
            logger.debug(f"Error getting Google Trend score for {product_name}: {e}")
            return 50  # Default reasonable score

    def calculate_demand_score(
        self,
        product_name: str,
        sold_listings: int,
        active_listings: int,
        avg_price: float,
    ) -> Dict[str, any]:
        """Calculate demand score based on multiple factors.
        
        Args:
            product_name: Product name
            sold_listings: Number of sold listings in period
            active_listings: Number of currently active listings
            avg_price: Average selling price
            
        Returns:
            Dictionary with demand metrics and score
        """
        result = {
            "product_name": product_name,
            "sold_listings": sold_listings,
            "active_listings": active_listings,
            "sold_to_active_ratio": sold_listings / active_listings if active_listings > 0 else 0,
            "avg_price": avg_price,
            "google_trend_score": None,
            "overall_demand_score": 0,
            "is_in_demand": False,
        }

        # Get Google Trends data
        time.sleep(1)  # Rate limiting for Google Trends
        google_score = self.get_google_trend_score(product_name)
        result["google_trend_score"] = google_score if google_score else 0

        # Calculate overall demand score (0-100)
        factors = []

        # Factor 1: Sold listings count (0-30 points)
        if sold_listings >= 100:
            factors.append(30)
        elif sold_listings >= 50:
            factors.append(25)
        elif sold_listings >= 20:
            factors.append(15)
        else:
            factors.append(max(0, sold_listings / 100 * 30))

        # Factor 2: Sold to active ratio (0-30 points)
        ratio = result["sold_to_active_ratio"]
        if ratio >= 2.5:
            factors.append(30)
        elif ratio >= 1.5:
            factors.append(25)
        elif ratio >= 1.0:
            factors.append(15)
        elif ratio >= 0.5:
            factors.append(10)
        else:
            factors.append(0)

        # Factor 3: Google Trends data (0-30 points)
        if google_score:
            factors.append((google_score / 100) * 30)
        
        # Factor 4: Price point (0-10 points) - mid-range items sell better
        if 20 <= avg_price <= 200:
            factors.append(10)
        elif 10 <= avg_price <= 500:
            factors.append(8)
        else:
            factors.append(5)

        result["overall_demand_score"] = sum(factors)
        
        # Determine if product is in demand based on multiple criteria
        result["is_in_demand"] = (
            sold_listings >= 20 and
            ratio >= 0.8 and
            (google_score and google_score >= 30 or google_score is None)
        )

        return result

    def validate_product(
        self,
        product_name: str,
        sold_count: int,
        active_count: int,
        avg_price: float,
    ) -> Dict:
        """Validate if product meets demand criteria."""
        return self.calculate_demand_score(
            product_name, sold_count, active_count, avg_price
        )
