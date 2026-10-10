import pytest
import requests
import responses

from posit.connect.sessions import Session


@responses.activate
def test_post_no_redirect():
    url = "https://connect.example.com/api"
    responses.add(responses.POST, url, json={"result": "ok"}, status=200)

    session = Session()
    response = session.post(url, data={"key": "value"})

    assert response.status_code == 200
    assert len(responses.calls) == 1
    assert responses.calls[0].request.method == "POST"


@responses.activate
def test_post_with_redirect_preserve():
    initial_url = "http://connect.example.com/api"
    redirect_url = "http://connect.example.com/redirect"

    responses.add(responses.POST, initial_url, status=302, headers={"location": "/redirect"})
    responses.add(responses.POST, redirect_url, json={"result": "redirected"}, status=200)

    session = Session()
    response = session.post(initial_url, data={"key": "value"}, preserve_post=True)

    assert response.status_code == 200
    assert len(responses.calls) == 2
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[1].request.method == "POST"
    # The final response should expose the redirect chain via history.
    assert len(response.history) == 1
    assert response.history[0].status_code == 302


@responses.activate
def test_post_with_redirect_no_preserve():
    initial_url = "http://connect.example.com/api"
    redirect_url = "http://connect.example.com/redirect"

    responses.add(responses.POST, initial_url, status=302, headers={"location": "/redirect"})
    responses.add(responses.GET, redirect_url, json={"result": "redirected"}, status=200)

    session = Session()
    response = session.post(initial_url, data={"key": "value"}, preserve_post=False)

    assert response.status_code == 200
    assert len(responses.calls) == 2
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[1].request.method == "GET"


@pytest.mark.parametrize("status_code", [307, 308])
@responses.activate
def test_post_redirect_307_308(status_code):
    initial_url = "http://connect.example.com/api"
    redirect_url = "http://connect.example.com/redirect"

    responses.add(
        responses.POST, initial_url, status=status_code, headers={"location": "/redirect"}
    )
    responses.add(responses.POST, redirect_url, json={"result": "redirected"}, status=200)

    session = Session()
    # Even with preserve_post=False, 307/308 preserve the method per RFC 7231.
    response = session.post(initial_url, data={"key": "value"}, preserve_post=False)

    assert response.status_code == 200
    assert len(responses.calls) == 2
    assert responses.calls[1].request.method == "POST"


@responses.activate
def test_post_redirect_max_redirects_raises():
    initial_url = "http://connect.example.com/api"
    redirect1_url = "http://connect.example.com/redirect1"
    redirect2_url = "http://connect.example.com/redirect2"

    responses.add(responses.POST, initial_url, status=302, headers={"location": "/redirect1"})
    responses.add(responses.POST, redirect1_url, status=302, headers={"location": "/redirect2"})
    responses.add(responses.POST, redirect2_url, status=302, headers={"location": "/redirect3"})

    session = Session()
    # Exceeding max_redirects now raises TooManyRedirects (the behavior of
    # requests.Session), instead of silently returning the last 3xx response.
    with pytest.raises(requests.exceptions.TooManyRedirects):
        session.post(initial_url, data={"key": "value"}, max_redirects=2, preserve_post=True)


@responses.activate
def test_post_redirect_no_location():
    url = "http://connect.example.com/api"
    responses.add(responses.POST, url, status=302, headers={})

    session = Session()
    response = session.post(url, data={"key": "value"})

    # With no Location header, requests stops following redirects.
    assert len(responses.calls) == 1
    assert response.status_code == 302


@responses.activate
def test_post_cross_origin_redirect_strips_authorization():
    """Session-level Authorization must not be forwarded across origins.

    This was the vulnerability that motivated the rewrite. Because the class
    now inherits ``SessionRedirectMixin.rebuild_auth``, cross-origin hops
    automatically drop the ``Authorization`` header.
    """
    initial_url = "https://connect.example.com/api"
    attacker_url = "https://attacker.example/collect"

    responses.add(responses.POST, initial_url, status=302, headers={"location": attacker_url})
    responses.add(responses.POST, attacker_url, json={}, status=200)

    session = Session()
    session.headers["Authorization"] = "Key super-secret"
    session.post(initial_url, data={"key": "value"}, preserve_post=True)

    assert len(responses.calls) == 2
    # First hop carries the credential; cross-origin follow-up must not.
    assert responses.calls[0].request.headers.get("Authorization") == "Key super-secret"
    assert "Authorization" not in responses.calls[1].request.headers


@responses.activate
def test_post_same_origin_redirect_preserves_authorization():
    initial_url = "https://connect.example.com/api"
    follow_url = "https://connect.example.com/next"

    responses.add(responses.POST, initial_url, status=302, headers={"location": "/next"})
    responses.add(responses.POST, follow_url, json={}, status=200)

    session = Session()
    session.headers["Authorization"] = "Key super-secret"
    session.post(initial_url, data={"key": "value"}, preserve_post=True)

    assert len(responses.calls) == 2
    assert responses.calls[0].request.headers.get("Authorization") == "Key super-secret"
    assert responses.calls[1].request.headers.get("Authorization") == "Key super-secret"
