def rename_params(params: dict) -> dict:
    """Rename params from the internal to the external signature.

    The API accepts `from` as a querystring parameter. Since `from` is a reserved word in Python, the SDK uses the name `start` instead. The querystring parameter `to` takes the same form for consistency.

    Parameters
    ----------
    params : dict

    Returns
    -------
    dict
    """
    if "start" in params:
        params["from"] = params["start"]
        del params["start"]

    if "end" in params:
        params["to"] = params["end"]
        del params["end"]

    return params
