#!/usr/bin/env python3
"""Quick demo runner for investor presentation."""

import json
import subprocess
import sys
from pathlib import Path

def run_quick_demo():
    """Run a quick analysis on best-performing products for demo."""
    
    # Products that typically show best results
    demo_products = [
        "vintage camera lens",
        "collectible trading cards",
        "gaming controller",
    ]
    
    print("\n" + "="*80)
    print("⚡ ARBITRAGE FINDER - QUICK DEMO")
    print("="*80)
    print(f"\nAnalyzing {len(demo_products)} products...")
    print("This demonstrates the system's ability to identify profitable arbitrage opportunities.\n")
    
    # Run the CLI
    cmd = [
        sys.executable,
        "cli.py",
    ] + demo_products + [
        "--output-format", "table",
        "--print-stats"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=str(Path(__file__).parent))
        
        if result.returncode == 0:
            print("\n✅ Demo completed successfully!")
            print("📊 Check results.json for detailed analysis\n")
            return True
        else:
            print("\n❌ Demo encountered an error")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        return False


if __name__ == "__main__":
    success = run_quick_demo()
    sys.exit(0 if success else 1)
