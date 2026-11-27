# Expense Tracker API (Copilot Code Review Demo)

A lightweight Python REST API (zero external dependencies) built for demonstrating automated testing, GitHub Copilot code review, branch workflow, and Pull Request merging.

## Files Included
- `expense_app.py`: Main HTTP server with `GET /health`, `GET /expenses`, and `POST /expenses`, including input validation.
- `expense_test.py`: Automated `unittest` suite testing valid entries and validation edge cases.
- `FIXED_SOLUTION.py`: Reference implementation after Copilot review & validation fixes.
- `VIDEO_GUIDE.md`: Step-by-step narration and screen guide for recording your walkthrough.

## Quick Run
1. Terminal 1: `python expense_app.py`
2. Terminal 2: `python expense_test.py`
