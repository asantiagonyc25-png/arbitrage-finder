#!/usr/bin/env python3
"""Display results summary."""

import json

try:
    with open('results.json', 'r') as f:
        data = json.load(f)
    
    print("=" * 80)
    print("✅ WINNING PRODUCTS FOUND")
    print("=" * 80)
    print(f"\nTotal Winners: {len(data)}\n")
    
    for i, product in enumerate(data, 1):
        print(f"{i}. {product['product_name'].upper()}")
        print(f"   Source: {product['source_platform']}")
        print(f"   eBay Selling Price: ${product['ebay_selling_price']:.2f}")
        print(f"   Landed Cost: ${product['landed_cost']:.2f}")
        print(f"   Profit per Unit: ${product['profit_per_unit']:.2f}")
        print(f"   Profit Margin: {product['profit_margin_percent']:.1f}%")
        print(f"   Demand Score: {product['ebay_demand_score']:.1f}/100")
        print(f"   Overall Score: {product['overall_score']:.1f}")
        print()
    
    print("=" * 80)
    
except Exception as e:
    print(f"Error: {e}")
