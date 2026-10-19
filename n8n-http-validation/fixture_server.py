"""Own synthetic loopback fixture. This is not Google Sheets or a client API."""
import json
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

calls = Counter()
rows = {}
events = []

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_json(self, status, body, headers=None):
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        for key, value in (headers or {}).items():
            self.send_header(key, str(value))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        route = urlparse(self.path)
        if route.path == "/state":
            return self.send_json(200, {"calls": dict(calls), "rows": rows, "events": events})
        if route.path != "/source":
            return self.send_json(404, {"error": "unknown route"})
        scenario = parse_qs(route.query).get("scenario", ["normal"])[0]
        calls[scenario] += 1
        if scenario == "rate-limit-once" and calls[scenario] == 1:
            return self.send_json(429, {"error": "synthetic rate limit"}, {"Retry-After": "1"})
        if scenario == "unavailable-once" and calls[scenario] == 1:
            return self.send_json(503, {"error": "synthetic unavailable"})
        if scenario == "permanent400":
            return self.send_json(400, {"error": "synthetic permanent input error"})
        if scenario == "always503":
            return self.send_json(503, {"error": "synthetic persistent failure"})
        records = [{"id": "item-a", "quantity": 10}, {"id": "item-b", "quantity": 5}]
        if scenario == "duplicate":
            records.insert(1, {"id": "item-a", "quantity": 999})
        if scenario == "missing-id":
            records.insert(1, {"quantity": 2})
        return self.send_json(200, {"records": records})

    def do_POST(self):
        if self.path == "/reset":
            calls.clear()
            rows.clear()
            events.clear()
            return self.send_json(200, {"reset": True})
        if self.path != "/row":
            return self.send_json(404, {"error": "unknown route"})
        length = int(self.headers.get("Content-Length", "0"))
        if length > 8192:
            return self.send_json(413, {"error": "fixture body limit"})
        try:
            row = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self.send_json(400, {"error": "invalid json"})
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            return self.send_json(422, {"error": "id required"})
        quantity = row.get("quantity")
        if type(quantity) is not int or quantity < 0:
            return self.send_json(422, {"error": "nonnegative integer quantity required"})
        existed = row["id"] in rows
        rows[row["id"]] = {"id": row["id"], "quantity": quantity}
        events.append({"id": row["id"], "quantity": quantity, "replaced": existed})
        return self.send_json(200, {"accepted": True, "replaced": existed})

if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    print(json.dumps({"host": "127.0.0.1", "port": server.server_port, "fixture": "synthetic-not-google-sheets"}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
