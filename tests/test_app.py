from app import MAX_MESSAGE_LENGTH, app, build_reply


def test_build_reply_handles_known_topics():
    assert "Flask" in build_reply("Tell me about flask")
    assert "Python" in build_reply("python")
    assert "Hello!" in build_reply("HI!")
    assert "Hello!" in build_reply("hey, there")
    assert build_reply("shipping") == "You said: shipping"


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


def test_ask_route_rejects_non_object_json():
    client = app.test_client()

    for payload in (["hello"], "hello", 42):
        response = client.post("/ask", json=payload)
        assert response.status_code == 400
        assert response.get_json() == {"error": "message is required"}


def test_ask_route_rejects_non_string_messages():
    client = app.test_client()

    for message in (42, True, ["hello"], {"text": "hello"}):
        response = client.post("/ask", json={"message": message})
        assert response.status_code == 400
        assert response.get_json() == {"error": "message must be a string"}


def test_ask_route_requires_message_text():
    client = app.test_client()

    for message in (None, "", "  \t  "):
        response = client.post("/ask", json={"message": message})
        assert response.status_code == 400
        assert response.get_json() == {"error": "message is required"}


def test_ask_route_rejects_oversized_messages():
    client = app.test_client()

    accepted = client.post("/ask", json={"message": "a" * MAX_MESSAGE_LENGTH})
    rejected = client.post("/ask", json={"message": "a" * (MAX_MESSAGE_LENGTH + 1)})

    assert accepted.status_code == 200
    assert rejected.status_code == 400
    assert rejected.get_json() == {
        "error": f"message must be {MAX_MESSAGE_LENGTH} characters or fewer"
    }


def test_ask_route_returns_reply():
    client = app.test_client()
    response = client.post("/ask", json={"message": "hello"})
    assert response.status_code == 200
    assert "reply" in response.get_json()


def test_ask_route_matches_whole_words_only():
    client = app.test_client()
    response = client.post("/ask", json={"message": "What is this python library?"})

    assert response.status_code == 200
    assert response.get_json()["reply"].startswith("Python is a great fit")
