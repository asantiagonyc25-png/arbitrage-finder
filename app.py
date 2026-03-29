"""Flask web app for the Arbitrage Finder - production deployment."""

import os
import json
import logging
from flask import Flask, render_template, jsonify, request
from datetime import datetime
from main import ArbitrageFinder

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Store results in memory
latest_results = {
    'status': 'idle',
    'products_analyzed': 0,
    'winning_products': [],
    'last_updated': None,
    'analysis_results': []
}


@app.route('/')
def index():
    """Serve the main dashboard."""
    return render_template('dashboard.html', results=latest_results)


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Run new analysis on provided products."""
    try:
        data = request.json
        products = data.get('products', [])
        
        if not products:
            return jsonify({'error': 'No products provided'}), 400
        
        # Run analysis
        finder = ArbitrageFinder()
        logger.info(f"Starting analysis of {len(products)} products...")
        
        latest_results['status'] = 'analyzing'
        latest_results['products_analyzed'] = len(products)
        latest_results['analysis_results'] = []
        latest_results['winning_products'] = []
        
        for product in products:
            result = finder.analyze_product(product, verbose=True)
            if result:
                latest_results['analysis_results'].append(result)
                if result.get('viable'):
                    latest_results['winning_products'].append(result)
        
        latest_results['status'] = 'complete'
        latest_results['last_updated'] = datetime.now().isoformat()
        
        # Load results.json if available
        try:
            with open('results.json', 'r') as f:
                file_results = json.load(f)
                latest_results['winning_products'] = file_results.get('winning_products', [])
        except:
            pass
        
        logger.info(f"Analysis complete: {len(latest_results['winning_products'])} winning products found")
        
        return jsonify({
            'status': 'success',
            'winning_products': latest_results['winning_products'],
            'total_analyzed': latest_results['products_analyzed']
        })
    
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        latest_results['status'] = 'error'
        return jsonify({'error': str(e)}), 500


@app.route('/api/results')
def get_results():
    """Get latest analysis results."""
    try:
        with open('results.json', 'r') as f:
            full_results = json.load(f)
            return jsonify(full_results)
    except:
        return jsonify(latest_results)


@app.route('/api/status')
def get_status():
    """Get current analysis status."""
    return jsonify({
        'status': latest_results['status'],
        'last_updated': latest_results['last_updated'],
        'products_analyzed': latest_results['products_analyzed'],
        'winning_products_count': len(latest_results['winning_products'])
    })


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    # Load any existing results
    try:
        with open('results.json', 'r') as f:
            file_results = json.load(f)
            latest_results['winning_products'] = file_results.get('winning_products', [])
            latest_results['last_updated'] = datetime.now().isoformat()
    except:
        pass
    
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
