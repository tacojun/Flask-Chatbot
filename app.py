import re

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


def build_reply(message: str) -> str:
    """Return a small deterministic reply for the demo chatbot."""
    normalized = message.strip().lower()

    if not normalized:
        return "Please type a message so I have something to respond to."
    words = set(re.findall(r"\b\w+\b", normalized))
    if words.intersection(("hello", "hi", "hey")):
        return "Hello! I'm a lightweight Flask chatbot demo."
    if "python" in words:
        return "Python is a great fit for small web services, automation, and data work."
    if "flask" in words:
        return "Flask keeps the web layer small and explicit, which makes it useful for prototypes and APIs."

    return f"You said: {message.strip()}"


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    """Return a minimal readiness response for deployment health checks."""
    return jsonify({"status": "ok"})


@app.post("/ask")
def ask():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "message is required"}), 400

    message = payload.get("message")
    if message is not None and not isinstance(message, str):
        return jsonify({"error": "message must be a string"}), 400

    if not message or not message.strip():
        return jsonify({"error": "message is required"}), 400

    return jsonify({"reply": build_reply(message)})


if __name__ == "__main__":
    app.run(debug=True)
