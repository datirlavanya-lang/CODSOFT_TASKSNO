"""
Rock, Paper, Scissors — Flask web app
--------------------------------------
All game logic lives in Python: picking the computer's move, deciding the
winner, and keeping score across rounds. The browser just sends the
player's choice and displays whatever Python sends back.

Run it with:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

import random

from flask import Flask, jsonify, render_template, request, session

app = Flask(__name__)
# A fixed key is fine for local/demo use. For a real deployment, set this
# from an environment variable instead of hardcoding it.
app.secret_key = "rock-paper-scissors-demo-key"

CHOICES = ("rock", "paper", "scissors")

# Each key beats the value it points to.
BEATS = {
    "rock": "scissors",
    "scissors": "paper",
    "paper": "rock",
}


def judge(user_choice, computer_choice):
    """Return 'user', 'computer', or 'tie'."""
    if user_choice == computer_choice:
        return "tie"
    if BEATS[user_choice] == computer_choice:
        return "user"
    return "computer"


def get_scores():
    session.setdefault("user_score", 0)
    session.setdefault("computer_score", 0)
    session.setdefault("ties", 0)
    session.setdefault("rounds", 0)
    return {
        "user_score": session["user_score"],
        "computer_score": session["computer_score"],
        "ties": session["ties"],
        "rounds": session["rounds"],
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/play", methods=["POST"])
def api_play():
    data = request.get_json(force=True, silent=True) or {}
    user_choice = data.get("choice")

    if user_choice not in CHOICES:
        return jsonify(error="Choose rock, paper, or scissors."), 400

    computer_choice = random.choice(CHOICES)
    outcome = judge(user_choice, computer_choice)

    scores = get_scores()
    scores["rounds"] += 1
    if outcome == "user":
        scores["user_score"] += 1
        message = "You win this round!"
    elif outcome == "computer":
        scores["computer_score"] += 1
        message = "Computer wins this round."
    else:
        scores["ties"] += 1
        message = "It's a tie!"

    session["user_score"] = scores["user_score"]
    session["computer_score"] = scores["computer_score"]
    session["ties"] = scores["ties"]
    session["rounds"] = scores["rounds"]

    return jsonify(
        user_choice=user_choice,
        computer_choice=computer_choice,
        outcome=outcome,
        message=message,
        scores=scores,
    )


@app.route("/api/reset", methods=["POST"])
def api_reset():
    session["user_score"] = 0
    session["computer_score"] = 0
    session["ties"] = 0
    session["rounds"] = 0
    return jsonify(scores=get_scores())


if __name__ == "__main__":
    app.run(debug=True)
