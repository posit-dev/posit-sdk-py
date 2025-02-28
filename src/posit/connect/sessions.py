from urllib.parse import urljoin

import requests


class Session(requests.Session):
    """Custom session that implements CURLOPT_POSTREDIR.

    This class mimics the functionality of CURLOPT_POSTREDIR from libcurl by
    providing a custom implementation of the POST method. It allows the caller
    to control whether the original POST data is preserved on redirects or if the
    request should be converted to a GET when a redirect occurs. This is achieved
    by disabling automatic redirect handling and manually following the redirect
    chain with the desired behavior.

    Notes
    -----
    The custom `post` method in this class:

    - Disables automatic redirect handling by setting ``allow_redirects=False``.
    - Manually follows redirects up to a specified ``max_redirects``.
    - Determines the HTTP method for subsequent requests based on the response
      status code and the ``preserve_post`` flag:

        - For HTTP status codes 307 and 308, the method and request body are
          always preserved as POST.
        - For other redirects (e.g., 301, 302, 303), the behavior is determined
          by ``preserve_post``:
            - If ``preserve_post=True``, the POST method is maintained.
            - If ``preserve_post=False``, the method is converted to GET and the
              request body is discarded.

    Examples
    --------
    Create a session and send a POST request while preserving POST data on redirects:

    >>> session = Session()
    >>> response = session.post(
    ...     "https://example.com/api", data={"key": "value"}, preserve_post=True
    ... )
    >>> print(response.status_code)

    See Also
    --------
    requests.Session : The base session class from the requests library.
    """

    def post(self, url, data=None, json=None, preserve_post=True, max_redirects=5, **kwargs):
        """
        Send a POST request and handle redirects manually.

        Parameters
        ----------
        url : str
            The URL to send the POST request to.
        data : dict, bytes, or file-like object, optional
            The form data to send.
        json : any, optional
            The JSON data to send.
        preserve_post : bool, optional
            If True, re-send POST data on redirects (mimicking CURLOPT_POSTREDIR);
            if False, converts to GET on 301/302/303 responses.
        max_redirects : int, optional
            Maximum number of redirects to follow.
        **kwargs
            Additional keyword arguments passed to the request.

        Returns
        -------
        requests.Response
            The final response after following redirects.
        """
        # Force manual redirect handling by disabling auto redirects.
        kwargs["allow_redirects"] = False

        # Initial POST request
        response = super().post(url, data=data, json=json, **kwargs)
        redirect_count = 0

        # Manually follow redirects, if any
        while response.is_redirect and redirect_count < max_redirects:
            redirect_url = response.headers.get("location")
            if not redirect_url:
                break  # No redirect URL; exit loop

            redirect_url = urljoin(response.url, redirect_url)

            # For 307 and 308 the HTTP spec mandates preserving the method and body.
            if response.status_code in (307, 308):
                method = "POST"
            else:
                if preserve_post:
                    method = "POST"
                else:
                    method = "GET"
                    data = None
                    json = None

            # Perform the next request in the redirect chain.
            response = self.request(method, redirect_url, data=data, json=json, **kwargs)
            redirect_count += 1

        return response
