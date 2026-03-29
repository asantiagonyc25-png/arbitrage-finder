#!/usr/bin/env python3
"""Test all imports to identify any issues."""

import sys

print("Testing imports...")

try:
    from ebay_scraper import EbayScraper
    print("✓ EbayScraper imported")
except Exception as e:
    print(f"✗ EbayScraper failed: {e}")

try:
    from demand_validator import DemandValidator
    print("✓ DemandValidator imported")
except Exception as e:
    print(f"✗ DemandValidator failed: {e}")

try:
    from source_marketplace_finder import SourceMarketplaceFinder
    print("✓ SourceMarketplaceFinder imported")
except Exception as e:
    print(f"✗ SourceMarketplaceFinder failed: {e}")

try:
    from shipping_calculator import ShippingCalculator
    print("✓ ShippingCalculator imported")
except Exception as e:
    print(f"✗ ShippingCalculator failed: {e}")

try:
    from profit_calculator import ProfitCalculator
    print("✓ ProfitCalculator imported")
except Exception as e:
    print(f"✗ ProfitCalculator failed: {e}")

try:
    from main import ArbitrageFinder
    print("✓ ArbitrageFinder imported")
except Exception as e:
    print(f"✗ ArbitrageFinder failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ All imports successful!")
