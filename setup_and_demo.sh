#!/bin/bash
# Quick setup and demo script for Arbitrage Finder

echo "=================================================="
echo "🚀 Arbitrage Finder - Setup & Demo"
echo "=================================================="
echo

# Check Python
echo "✓ Checking Python installation..."
python3 --version || { echo "❌ Python3 is required. Install from python.org"; exit 1; }

# Install dependencies
echo "✓ Installing dependencies... (this may take a minute)"
python3 -m pip install -q requests beautifulsoup4 pytrends python-dotenv lxml fake-useragent

echo "✓ Dependencies installed"
echo

# Run demo
echo "✓ Running demo analysis..."
echo "  Analyzing: Vintage Camera Lens, Gaming Controller, Trading Cards"
echo

python3 cli.py "vintage camera lens" "gaming controller" "collectible trading cards" \
    --output-format table --print-stats

echo
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo
echo "Next steps:"
echo "1. Review the results above and in results.json"
echo "2. Read INVESTOR_OVERVIEW.md for business details"
echo "3. Run: python3 cli.py --help"
echo "4. Try: python3 cli.py 'your product here'"
echo
