# Deployment Guide: Getting Your Arbitrage Finder Live

## Quick Option: Deploy with ngrok (30 seconds)

The easiest way to get a public, shareable link immediately:

### 1. Install ngrok
```bash
# Via Homebrew (macOS)
brew install ngrok

# Or download from https://ngrok.com/download
```

### 2. Start the app (if not running)
```bash
cd /Users/alexandersantiago/Desktop/Projects/project-112
source .venv/bin/activate
PORT=8080 python3 app.py
```

### 3. Expose with ngrok (in another terminal)
```bash
ngrok http 8080
```

This will give you a public URL like: `https://abc123def.ngrok.io`

---

## Production Option: Deploy to Railway.app (2 minutes)

1. Sign up at https://railway.app (free tier available)
2. Create new project → GitHub/Docker → Select this repository
3. Railway automatically detects the `Procfile` and `requirements.txt`
4. Get your public URL: `https://your-app-name.railway.app`

**Environment Variables (optional):**
- `PORT`: Leave default, Railway handles it

---

## Alternative: Deploy to Render.com

1. Go to https://render.com
2. Connect GitHub
3. Create new "Web Service"
4. Select this repo
5. Select "Python 3" → Deploy

---

## Alternative: Deploy to Heroku (Classic)

```bash
# Install Heroku CLI
brew install heroku

# Login
heroku login

# Create app
heroku create arbitrage-finder-YOUR-NAME

# Deploy
git push heroku main

# Get URL
heroku open
```

---

## Testing Locally

While developing/testing locally, the app runs at:
- URL: http://localhost:8080
- Dashboard: http://localhost:8080/
- API: http://localhost:8080/api/analyze (POST)

### Run local analysis:
```bash
curl -X POST http://localhost:8080/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "products": ["LED light bulbs", "USB cables"]
  }'
```

---

## Architecture

The system has these real-time components:

1. **Real eBay Scraper** (`real_ebay_scraper.py`)
   - Scrapes live eBay search results
   - Extracts active listings, sold count, average price
   - Rate-limited to avoid blocking

2. **Demand Validator** (`demand_validator.py`)
   - Checks Google Trends data
   - Analyzes sold-to-active ratio
   - Scores product viability 0-100

3. **Source Marketplace Finder** (`source_marketplace_finder.py`)
   - Searches 1688, Taobao, Alibaba, Yahoo Auctions JP, Mercari JP
   - Finds lowest wholesale prices

4. **Shipping Calculator** (`shipping_calculator.py`)
   - Computes landed cost (item + shipping + fees + duties + taxes)
   - Accurate to real-world physics

5. **Profit Calculator** (`profit_calculator.py`)
   - eBay fees, PayPal fees, packaging, misc costs
   - 30% minimum margin threshold

6. **Flask Web App** (`app.py`)
   - REST API for analysis
   - Beautiful responsive dashboard
   - Real-time results

---

## Data Flow

```
User Input (product names)
    ↓
Real eBay Scraper (gets live data)
    ↓
Demand Validator (checks if worth analyzing)
    ↓
Source Marketplace Finder (searches suppliers)
    ↓
Shipping Calculator (computes landed cost)
    ↓
Profit Calculator (determines margins) 
    ↓
Results JSON 
    ↓
Dashboard Display
```

---

## API Endpoints

### POST `/api/analyze`
Analyze products and get results.

**Request:**
```json
{
  "products": ["LED light bulbs", "USB cables", "Phone cases"]
}
```

**Response:**
```json
{
  "status": "success",
  "winning_products": [
    {
      "product_name": "LED light bulbs",
      "source": "1688",
      "ebay_price": 155.00,
      "source_cost": 39.05,
      "landed_cost": 48.13,
      "profit_per_unit": 106.87,
      "profit_margin": 68.9,
      "demand_score": 75
    }
  ],
  "total_analyzed": 3
}
```

### GET `/api/results`
Get latest analysis results (cached from `results.json`)

### GET `/api/status`
Get current analysis status

### GET `/health`
Health check for monitoring/uptime

---

## Tips for Better Results

1. **Use specific product names:**
   - ✅ "LED 5050 RGB light strips" 
   - ❌ "lights"

2. **Look for niches:**
   - Electronics accessories (cables, adapters, chargers)
   - Smart home items (bulbs, plugs, speakers)
   - Phone/laptop protection
   - Gaming peripherals

3. **Monitor regularly:**
   - Market demand changes daily
   - Prices fluctuate on supplier sites
   - Competition affects margins

4. **Verify results:**
   - Always check listings manually on eBay
   - Confirm supplier availability on 1688/Taobao  
   - Verify shipping costs to your location

---

## Troubleshooting

**"eBay data extraction failed"**
- eBay blocks at certain rates
- System falls back to realistic estimates
- Try different products
- Wait a few minutes between runs

**"No winning products found"**
- Product might not have enough demand
- Margins too thin on that item
- Try more specific product names
- Try trending electronics

**App won't start**
- Check Python 3.8+: `python3 --version`
- Install dependencies: `pip install -r requirements.txt`
- Kill old processes: `lsof -ti :8080 | xargs kill -9`

**API returns empty results**
- Initial run is slow (~30-60 seconds per product)
- Check `results.json` for cached previous results
- Check logs for specific errors

---

## What's Real vs Estimated

✅ **REAL (Live Data):**
- eBay search counts (active listings)
- eBay sold listings count
- Average selling prices on eBay
- Google Trends demand signals
- Shipping calculator logic
- Fee calculations

⚠️ **ESTIMATED (when actual data unavailable):**
- Source marketplace prices (when scrape fails)
- Sold-to-active ratios (fallback)
- Market velocity estimates

The system is **production-capable** but should be monitored for:
- eBay rate limiting (system has fallbacks)
- Source site changes (1688, Taobao)
- Market volatility (prices change hourly)

---

## Next Steps

1. Deploy using ngrok for instant public URL
2. Share the link with investors
3. Run analyses on target products  
4. Move to production hosting (Railway, Render, Heroku)
5. Add authentication for production use
6. Set up scheduled monitoring/alerts

---

Questions? Check the logs or create more detailed analysis with `--verbose` flag.
