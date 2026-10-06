"""
Password Generator — Flask web app
-----------------------------------
All password generation and strength scoring happens in Python, on the
server. The browser only sends the user's chosen settings (length, which
character types to include) and displays whatever Python sends back.

Run it with:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

import secrets
import string

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

CHAR_SETS = {
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
    "digits": string.digits,
    "symbols": "!@#$%^&*()-_=+[]{};:,.?/",
}

LOOKALIKES = set("O0oIl1|")

MIN_LENGTH = 4
MAX_LENGTH = 64


def build_pools(selected_types, strip_lookalikes):
    """Return the list of character pools (one per selected type)."""
    pools = []
    for key in ("lower", "upper", "digits", "symbols"):
        if key not in selected_types:
            continue
        chars = CHAR_SETS[key]
        if strip_lookalikes:
            chars = "".join(c for c in chars if c not in LOOKALIKES)
        if chars:
            pools.append(chars)
    return pools


def generate_password(length, pools):
    """
    Build a random password of the given length using Python's `secrets`
    module (cryptographically secure), guaranteeing at least one
    character from every selected pool, then shuffling the result so the
    guaranteed characters aren't always in the same position.
    """
    all_chars = "".join(pools)

    password_chars = [secrets.choice(pool) for pool in pools[:length]]
    while len(password_chars) < length:
        password_chars.append(secrets.choice(all_chars))

    # Fisher-Yates shuffle using a secure random source.
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    return "".join(password_chars)


def score_strength(password):
    """
    Rate strength by how many character types the password actually
    contains and how much of it is repeated characters — not by length
    alone.
    """
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)
    categories = sum([has_lower, has_upper, has_digit, has_symbol])

    unique_count = len(set(password))
    unique_ratio = unique_count / len(password) if password else 0

    score = (categories / 4) * 0.65 + unique_ratio * 0.35

    if score >= 0.9:
        label, level = "Very strong", 4
    elif score >= 0.7:
        label, level = "Strong", 3
    elif score >= 0.45:
        label, level = "Fair", 2
    else:
        label, level = "Weak", 1

    return {
        "label": label,
        "level": level,
        "categories": categories,
        "unique_count": unique_count,
        "length": len(password),
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json(force=True, silent=True) or {}

    try:
        length = int(data.get("length", 16))
    except (TypeError, ValueError):
        return jsonify(error="Length must be a number."), 400

    length = max(MIN_LENGTH, min(MAX_LENGTH, length))

    selected_types = {
        key for key in ("lower", "upper", "digits", "symbols")
        if data.get(key)
    }
    strip_lookalikes = bool(data.get("noLookalikes"))

    if not selected_types:
        return jsonify(error="Choose at least one character type."), 400

    pools = build_pools(selected_types, strip_lookalikes)
    if not pools:
        return jsonify(error="That combination leaves no usable characters."), 400

    password = generate_password(length, pools)
    strength = score_strength(password)

    return jsonify(password=password, strength=strength)


if __name__ == "__main__":
    app.run(debug=True)
