#!/usr/bin/env python3
"""Simple web server to display Arbitrage Finder results."""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

os.chdir(Path(__file__).parent)

print("=" * 60)
print("🚀 Arbitrage Finder Web Server")
print("=" * 60)
print(f"\n📱 Opening website at: http://localhost:{PORT}")
print(f"   Click link above or paste in your browser\n")
print("Type CTRL+C to stop the server\n")
print("=" * 60)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    # Open browser automatically
    webbrowser.open(f'http://localhost:{PORT}/')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
