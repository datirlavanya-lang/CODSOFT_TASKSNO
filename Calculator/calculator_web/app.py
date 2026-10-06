"""
Calculator — Flask web app
----------------------------
The two numbers and the chosen operation are sent from the browser, but
every calculation happens here, in Python. The browser only displays
whatever Python sends back.

Run it with:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

OPERATIONS = {
    "add": lambda a, b: a + b,
    "subtract": lambda a, b: a - b,
    "multiply": lambda a, b: a * b,
    "divide": lambda a, b: a / b,
}

SYMBOLS = {
    "add": "+",
    "subtract": "-",
    "multiply": "×",
    "divide": "÷",
}


def calculate(num1, num2, operation):
    """Perform the calculation in Python and return the numeric result."""
    if operation not in OPERATIONS:
        raise ValueError("Unknown operation.")
    if operation == "divide" and num2 == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return OPERATIONS[operation](num1, num2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    data = request.get_json(force=True, silent=True) or {}

    try:
        num1 = float(data.get("num1"))
        num2 = float(data.get("num2"))
    except (TypeError, ValueError):
        return jsonify(error="Both inputs need to be numbers."), 400

    operation = data.get("operation")

    try:
        result = calculate(num1, num2, operation)
    except ZeroDivisionError as e:
        return jsonify(error=str(e)), 400
    except ValueError as e:
        return jsonify(error=str(e)), 400

    # Show whole numbers cleanly (e.g. 4 instead of 4.0) while keeping
    # decimals when the result actually has them.
    if result == int(result) and abs(result) < 1e15:
        result_display = int(result)
    else:
        result_display = round(result, 10)

    return jsonify(
        result=result_display,
        num1=num1,
        num2=num2,
        operation=operation,
        symbol=SYMBOLS[operation],
    )


if __name__ == "__main__":
    app.run(debug=True)
