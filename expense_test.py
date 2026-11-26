import json
import unittest
import urllib.error
import urllib.request


def request_json(url: str, method: str = "GET", payload: object | None = None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=3) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


class TestExpenseTracker(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000"

    def test_add_valid_expense(self):
        status, body = request_json(
            f"{self.BASE_URL}/expenses",
            method="POST",
            payload={"title": "  Coffee  ", "amount": 450, "category": "  Food  "},
        )
        self.assertEqual(status, 201)
        self.assertEqual(body["title"], "Coffee")
        self.assertEqual(body["category"], "food")

    def test_whitespace_title_trimmed(self):
        status, body = request_json(
            f"{self.BASE_URL}/expenses",
            method="POST",
            payload={"title": "  Fuel  ", "amount": 2500, "category": "Transport"},
        )
        self.assertEqual(status, 201)
        self.assertEqual(body["title"], "Fuel")

    def test_empty_title_returns_400(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            request_json(
                f"{self.BASE_URL}/expenses",
                method="POST",
                payload={"title": "   ", "amount": 500},
            )
        self.assertEqual(ctx.exception.code, 400)

    def test_negative_or_zero_amount_returns_400(self):
        for amount in (-100, 0):
            with self.subTest(amount=amount):
                with self.assertRaises(urllib.error.HTTPError) as ctx:
                    request_json(
                        f"{self.BASE_URL}/expenses",
                        method="POST",
                        payload={"title": "Invalid Item", "amount": amount},
                    )
                self.assertEqual(ctx.exception.code, 400)

    def test_invalid_json_returns_400(self):
        req = urllib.request.Request(
            f"{self.BASE_URL}/expenses",
            data=b'{"title":',
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req, timeout=3)
        self.assertEqual(ctx.exception.code, 400)

    def test_non_object_json_returns_400(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            request_json(
                f"{self.BASE_URL}/expenses",
                method="POST",
                payload=["not", "an", "object"],
            )
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
