"""Small readiness endpoint; no server is started on import."""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Health:
    def __init__(self):
        self.last_success = 0.0

    def ready(self):
        return time.monotonic() - self.last_success < 90 and self.last_success > 0

    def mark_ready(self):
        self.last_success = time.monotonic()

    def unavailable(self):
        self.last_success = 0.0


def start_health_server(health, port):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in ("/", "/health"):
                self.send_error(404)
                return
            ready = health.ready()
            body = json.dumps({"status": "ready" if ready else "unavailable"}).encode()
            self.send_response(200 if ready else 503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
