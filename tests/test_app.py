from app import app, build_reply


def test_build_reply_handles_known_topics():
    assert "Flask" in build_reply("Tell me about flask")
    assert "Python" in build_reply("python")


def test_index_route_returns_html():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Chatbot" in response.data


def test_health_route_returns_ok():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_ask_route_validates_input():
    client = app.test_client()
    response = client.post("/ask", json={"message": ""})
    assert response.status_code == 400
    assert response.get_json()["error"] == "message is required"


def test_ask_route_returns_reply():
    client = app.test_client()
    response = client.post("/ask", json={"message": "hello"})
    assert response.status_code == 200
    assert "reply" in response.get_json()
