"""
Simple HTTP Server for Frontend

Run this to serve the frontend on http://localhost:8080

Usage:
    python frontend_server.py
"""

import http.server
import socketserver
import os
from pathlib import Path
from urllib.parse import unquote

PORT_CANDIDATES = [8080, 8081, 8082, 9000]
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
PATIENT_DIR = Path(FRONTEND_DIR).parent / 'Patient_001_Lakshmi'

# Allow quick restarts on Windows without stale socket errors.
socketserver.TCPServer.allow_reuse_address = True

class FrontendHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def do_GET(self):
        # Serve index.html for all requests (SPA routing)
        if self.path.startswith('/patient-assets/'):
            relative_path = unquote(self.path.removeprefix('/patient-assets/').split('?', 1)[0])
            requested_path = (PATIENT_DIR / relative_path).resolve()
            if PATIENT_DIR.resolve() not in requested_path.parents:
                self.send_error(403)
                return
            self.path = '/' + str(requested_path.relative_to(Path(FRONTEND_DIR).parent)).replace('\\', '/')
            self.directory = str(Path(FRONTEND_DIR).parent)
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        
        return super().do_GET()

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == '__main__':
    os.chdir(FRONTEND_DIR)

    httpd = None
    for port in PORT_CANDIDATES:
        try:
            httpd = ThreadedTCPServer(("", port), FrontendHandler)
            break
        except OSError:
            continue

    if httpd is None:
        raise RuntimeError("Could not bind the frontend server to any candidate port (8080, 8081, 8082, 9000).")

    PORT = httpd.server_address[1]
    print(f"Frontend server running at http://localhost:{PORT}")
    print(f"Serving from: {FRONTEND_DIR}")
    print(f"Open http://localhost:{PORT} in your browser")
    print(f"Make sure backend is running on http://localhost:8000")
    print(f"\nPress Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    finally:
        httpd.server_close()
