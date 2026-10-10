import requests


class Session(requests.Session):
    """Custom session that preserves POST bodies across 301/302 redirects.

    RFC 7231 allows clients to downgrade POST to GET on 301/302, and
    ``requests`` does so by default. Some Connect endpoints issue a 302 and
    expect the client to re-POST the original body to the new location
    (mirroring libcurl's ``CURLOPT_POSTREDIR`` behavior). Overriding
    :meth:`rebuild_method` keeps every other piece of the ``requests``
    redirect machinery intact — ``rebuild_auth`` (which strips the
    ``Authorization`` header on cross-origin hops), cookie propagation,
    ``response.history``, ``TooManyRedirects``, proxy rebuild, and streaming
    semantics — so this class is a minimal, safe override rather than a
    hand-rolled redirect loop.
    """

    def __init__(self):
        super().__init__()
        self._preserve_post_on_redirect = True

    def rebuild_method(self, prepared_request, response):
        """Preserve POST across 301/302 when ``preserve_post_on_redirect`` is set.

        303 always downgrades to GET per the HTTP spec. 307/308 already
        preserve the method in the base implementation.
        """
        if (
            self._preserve_post_on_redirect
            and prepared_request.method == "POST"
            and response.status_code in (301, 302)
        ):
            return
        super().rebuild_method(prepared_request, response)

    def post(self, url, data=None, json=None, preserve_post=True, max_redirects=5, **kwargs):
        """Send a POST request.

        Parameters
        ----------
        url : str
            The URL to send the POST request to.
        data : dict, bytes, or file-like object, optional
            The form data to send.
        json : any, optional
            The JSON data to send.
        preserve_post : bool, optional
            If True (default), re-send POST data on 301/302 redirects
            (mimicking ``CURLOPT_POSTREDIR``). If False, fall back to the
            default ``requests`` behavior (downgrade to GET on 301/302).
        max_redirects : int, optional
            Maximum number of redirects to follow before raising
            :class:`requests.exceptions.TooManyRedirects`.
        **kwargs
            Additional keyword arguments passed to :meth:`requests.Session.request`.
        """
        previous_preserve = self._preserve_post_on_redirect
        previous_max = self.max_redirects
        self._preserve_post_on_redirect = preserve_post
        self.max_redirects = max_redirects
        try:
            return super().post(url, data=data, json=json, **kwargs)
        finally:
            self._preserve_post_on_redirect = previous_preserve
            self.max_redirects = previous_max
