import os
import signal
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.getenv("PORT", "10000"))
bot = None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/health", "/healthz"):
            body = b"videoplayer is running"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        pass

def stop_bot(*_):
    global bot
    if bot and bot.poll() is None:
        bot.terminate()
        try:
            bot.wait(timeout=10)
        except subprocess.TimeoutExpired:
            bot.kill()

def main():
    global bot
    signal.signal(signal.SIGTERM, stop_bot)
    signal.signal(signal.SIGINT, stop_bot)
    bot = subprocess.Popen(["python3", "main.py"])
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        while bot.poll() is None:
            thread.join(timeout=1)
        raise SystemExit(bot.returncode or 0)
    finally:
        server.shutdown()
        server.server_close()
        stop_bot()

if __name__ == "__main__":
    main()
