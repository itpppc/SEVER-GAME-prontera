# -*- coding: utf-8 -*-
"""
Production Multi-Threaded HTTP Server for Bangkok Transit & Mobility Dashboard.
Provides high performance, UTF-8 encoding, and instant browser opening.
"""
import http.server
import socketserver
import os
import sys
import webbrowser

PORT = 5555
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class ProductionHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def guess_type(self, path):
        ctype = super().guess_type(path)
        if ctype.startswith('text/') or ctype in ['application/javascript', 'application/json']:
            return f"{ctype}; charset=utf-8"
        return ctype

    def log_message(self, format, *args):
        # Clean logging
        print(f"[ProductionServer] {self.address_string()} - {format % args}")

def run_server():
    global PORT
    handler = ProductionHandler
    
    # Try preferred port, if busy increment
    for p in range(PORT, PORT + 20):
        try:
            httpd = socketserver.ThreadingTCPServer(('127.0.0.1', p), handler)
            PORT = p
            break
        except OSError:
            continue
    else:
        print("ERROR: Could not bind to any available port in range.")
        sys.exit(1)

    url = f"http://localhost:{PORT}/index.html"
    print("=" * 65)
    print("   BANGKOK MOBILITY & TRANSIT DASHBOARD - PRODUCTION SERVICE")
    print("=" * 65)
    print(f" * Server Status: RUNNING (Production Threaded)")
    print(f" * Local URL:     {url}")
    print(f" * Root Path:     {DIRECTORY}")
    print(f" * Port:          {PORT}")
    print("=" * 65)
    print("Press Ctrl+C to stop the server anytime.")
    print("Opening browser...")

    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Note: Could not auto-launch browser ({e}). Please open {url} manually.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Production Server...")
        httpd.server_close()
        print("Production Server stopped gracefully.")

if __name__ == '__main__':
    run_server()
