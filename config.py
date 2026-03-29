"""Configuration and constants for the arbitrage finder."""

# eBay Settings
EBAY_SEARCH_CATEGORIES = [
    "Electronics",
    "Home & Garden",
    "Sports",
    "Collectibles",
    "Fashion",
]

# Demand thresholds
MIN_SOLD_LISTINGS = 50  # Minimum sold listings in last 90 days
MIN_SOLD_TO_ACTIVE_RATIO = 1.5  # Sold listings / Active listings ratio
MIN_GOOGLE_TREND_SCORE = 40  # Google Trends interest score (0-100)

# Profit margin thresholds
MIN_PROFIT_MARGIN_PERCENT = 30  # Minimum 30% profit margin
MIN_PROFIT_DOLLAR = 10  # Minimum $10 profit

# Source platforms
SOURCE_PLATFORMS = {
    "taobao": "https://taobao.com",
    "1688": "https://1688.com",
    "alibaba": "https://alibaba.com",
    "yahoo_auctions": "https://auctions.yahoo.co.jp",
    "japan_auctions": "https://ja.mercari.com",
}

# Shipping aggregators
SHIPPING_PROVIDERS = {
    "china": ["mulebuy", "superbuy"],
    "japan": ["buyee", "zenmarket"],
}

# eBay API endpoints
EBAY_API_BASE = "https://api.ebay.com"

# Rate limiting
REQUESTS_PER_SECOND = 2
TIMEOUT_SECONDS = 10
MAX_RETRIES = 3
