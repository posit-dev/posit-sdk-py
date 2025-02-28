import pytest
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
    # Confirm that the request method was POST.
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

    # Both calls should use the POST method.
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[1].request.method == "POST"


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
    # The initial call is a POST, but the follow-up should be a GET since preserve_post is False
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[1].request.method == "GET"


@pytest.mark.parametrize("status_code", [307, 308])
@responses.activate
def test_post_redirect_307_308(status_code):
    initial_url = "http://connect.example.com/api"
    redirect_url = "http://connect.example.com/redirect"

    # For 307 and 308 redirects, the HTTP spec mandates preserving the method.
    responses.add(
        responses.POST, initial_url, status=status_code, headers={"location": "/redirect"}
    )
    responses.add(responses.POST, redirect_url, json={"result": "redirected"}, status=200)

    session = Session()
    # Even with preserve_post=False, a 307 or 308 redirect should use POST.
    response = session.post(initial_url, data={"key": "value"}, preserve_post=False)

    assert response.status_code == 200
    assert len(responses.calls) == 2
    # Confirm that the method for the redirect is still POST.
    assert responses.calls[1].request.method == "POST"


@responses.activate
def test_post_redirect_max_redirects():
    initial_url = "http://connect.example.com/api"
    redirect1_url = "http://connect.example.com/redirect1"
    redirect2_url = "http://connect.example.com/redirect2"

    # Build a chain of 3 redirects.
    responses.add(responses.POST, initial_url, status=302, headers={"location": "/redirect1"})
    responses.add(responses.POST, redirect1_url, status=302, headers={"location": "/redirect2"})
    responses.add(responses.POST, redirect2_url, status=302, headers={"location": "/redirect3"})

    session = Session()
    # Limit to 2 redirects; thus, the third redirect response should not be followed.
    response = session.post(
        initial_url, data={"key": "value"}, max_redirects=2, preserve_post=True
    )

    # The calls should include: initial, first redirect, and second redirect.
    assert len(responses.calls) == 3
    # The final response is the one from the second redirect.
    assert response.status_code == 302
    # The Location header should point to the third URL.
    assert response.headers.get("location") == "/redirect3"


@responses.activate
def test_post_redirect_no_location():
    url = "http://connect.example.com/api"
    # Simulate a redirect response that lacks a Location header.
    responses.add(responses.POST, url, status=302, headers={})

    session = Session()
    response = session.post(url, data={"key": "value"})

    # The loop should break immediately since there is no location to follow.
    assert len(responses.calls) == 1
    assert response.status_code == 302


@responses.activate
def test_post_redirect_location_none_explicit():
    url = "http://connect.example.com/api"

    # Use a callback to explicitly return a None for the "location" header.
    def request_callback(request):
        return (302, {"location": ""}, "Redirect without location")

    responses.add_callback(responses.POST, url, callback=request_callback)

    session = Session()
    response = session.post(url, data={"key": "value"})

    # The redirect loop should break since location is None.
    assert len(responses.calls) == 1
    assert response.status_code == 302
