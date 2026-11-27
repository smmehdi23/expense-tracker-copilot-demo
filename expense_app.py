import json
import math
from http.server import BaseHTTPRequestHandler, HTTPServer

EXPENSES = []


class ValidationError(ValueError):
    pass


def add_expense(title: str, amount: float, category: str = "general") -> dict:
    if not isinstance(title, str):
        raise ValidationError("title must be a string")
    title = title.strip()
    if not title:
        raise ValidationError("title must not be empty")

    if (
        isinstance(amount, bool)
        or not isinstance(amount, (int, float))
        or (isinstance(amount, float) and not math.isfinite(amount))
        or amount <= 0
    ):
        raise ValidationError("amount must be a positive number")

    if not isinstance(category, str):
        raise ValidationError("category must be a string")
    category = category.strip().lower()
    if not category:
        raise ValidationError("category must not be empty")

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

        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            self._send_json(400, {"error": "Invalid Content-Length"})
            return
        if content_length < 0:
            self._send_json(400, {"error": "Invalid Content-Length"})
            return

        try:
            raw_body = self.rfile.read(content_length)
            data = json.loads(raw_body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "Invalid JSON request"})
            return

        if not isinstance(data, dict):
            self._send_json(400, {"error": "JSON body must be an object"})
            return

        try:
            created = add_expense(
                data.get("title"),
                data.get("amount"),
                data.get("category", "general"),
            )
        except ValidationError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        self._send_json(201, created)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), ExpenseHandler)
    print("Expense Tracker running on http://127.0.0.1:8000")
    server.serve_forever()
