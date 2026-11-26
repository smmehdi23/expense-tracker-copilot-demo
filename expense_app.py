import json
from http.server import BaseHTTPRequestHandler, HTTPServer

EXPENSES = []


def add_expense(title: str, amount: float, category: str = "general") -> dict:
    # Intentional edge-case bug for Copilot code review demo:
    # - Doesn't strip whitespace or reject empty titles
    # - Allows negative or zero amounts
    # - Doesn't normalize category casing
    item = {
        "id": len(EXPENSES) + 1,
        "title": title,
        "amount": amount,
        "category": category,
    }
    EXPENSES.append(item)
    return item


class ExpenseHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "count": len(EXPENSES)})
        elif self.path == "/expenses":
            total = sum(e["amount"] for e in EXPENSES)
            self._send_json(200, {"expenses": EXPENSES, "total": round(total, 2)})
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/expenses":
            self._send_json(404, {"error": "Not found"})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)
        data = json.loads(raw_body.decode("utf-8"))

        title = data.get("title")
        amount = data.get("amount")
        category = data.get("category", "general")

        created = add_expense(title, amount, category)
        self._send_json(201, created)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), ExpenseHandler)
    print("Expense Tracker running on http://127.0.0.1:8000")
    server.serve_forever()
