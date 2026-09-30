from threading import Thread

import pytest
from playwright.sync_api import expect, sync_playwright
from werkzeug.serving import make_server

import app as application


@pytest.fixture(scope="module")
def server_url():
    server = make_server("127.0.0.1", 0, application.app, threaded=True)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(browser, server_url):
    context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
    page = context.new_page()
    page.goto(server_url)
    yield page
    context.close()


def paste_message(page, message):
    # A native paste exercises maxlength; assigning value or fill() can bypass it.
    page.evaluate("text => navigator.clipboard.writeText(text)", message)
    page.locator("#user-input").click()
    page.keyboard.press("Control+V")
    expect(page.locator("#user-input")).to_have_value(message)


def send_message(page, message):
    with page.expect_response(
        lambda response: response.url.endswith("/ask")
        and response.request.method == "POST"
    ) as pending:
        page.get_by_role("button", name="Send", exact=True).click()
    response = pending.value
    assert response.request.post_data_json == {"message": message}
    assert response.status == 200
    assert response.json() == {"reply": f"You said: {message}"}
    expect(page.locator(".message.user")).to_have_text(message)
    expect(page.locator(".message.bot")).to_have_text(f"You said: {message}")


@pytest.mark.parametrize("character", ["a", "ğ", "😀"])
@pytest.mark.parametrize("length", [999, 1000, 1001])
def test_native_paste_preserves_message_and_enforces_boundary(page, character, length):
    message = character * length
    requests = []
    page.on("request", lambda request: requests.append(request) if request.url.endswith("/ask") else None)
    paste_message(page, message)

    if length <= application.MAX_MESSAGE_LENGTH:
        send_message(page, message)
    else:
        page.get_by_role("button", name="Send", exact=True).click()
        assert not page.locator("#user-input").evaluate("input => input.checkValidity()")
        expect(page.locator("#user-input")).to_have_value(message)
        expect(page.locator(".message")).to_have_count(0)
        assert requests == []


def test_editing_invalid_message_allows_submission(page):
    paste_message(page, "😀" * (application.MAX_MESSAGE_LENGTH + 1))
    assert not page.locator("#user-input").evaluate("input => input.checkValidity()")
    page.keyboard.press("Backspace")
    expect(page.locator("#user-input")).to_have_value("😀" * application.MAX_MESSAGE_LENGTH)
    assert page.locator("#user-input").evaluate("input => input.checkValidity()")
    send_message(page, "😀" * application.MAX_MESSAGE_LENGTH)


def test_browser_counts_the_trimmed_message_it_sends(page):
    message = "😀" * application.MAX_MESSAGE_LENGTH
    paste_message(page, f"  {message}  ")
    send_message(page, message)


def test_browser_uses_configured_server_limit(page, server_url, monkeypatch):
    monkeypatch.setattr(application, "MAX_MESSAGE_LENGTH", 3)
    page.goto(server_url)
    paste_message(page, "😀" * 3)
    send_message(page, "😀" * 3)
    paste_message(page, "😀" * 4)
    assert not page.locator("#user-input").evaluate("input => input.checkValidity()")
    response = application.app.test_client().post("/ask", json={"message": "😀" * 4})
    assert response.status_code == 400
