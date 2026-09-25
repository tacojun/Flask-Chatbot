# Flask Chatbot

A small, dependency-light chatbot demo built with Flask. The first working version is intentionally deterministic and does not require external API keys, which makes it easy to run, test, and extend.

## Features

- Flask web server
- JSON `/ask` endpoint
- JSON `/health` endpoint for deployment probes
- Responsive browser UI
- Input validation and error handling
- Deterministic reply engine for local development
- Automated tests with pytest

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Run tests

```bash
pytest
```

## API

Send a chat message:

```bash
curl -X POST http://127.0.0.1:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'
```

Example response:

```json
{"reply":"Hello! I'm a lightweight Flask chatbot demo."}
```

Check service health:

```bash
curl http://127.0.0.1:5000/health
```

A healthy process responds with HTTP 200 and:

```json
{"status":"ok"}
```

## Project structure

```text
app.py
requirements.txt
templates/
  index.html
static/
  style.css
tests/
  test_app.py
```

## Roadmap

- optional external LLM provider integration behind an adapter
- conversation history
- rate limiting
- deployment documentation

## Security

Do not commit API keys or other secrets. Future provider integrations should read credentials from environment variables or a secret manager.
