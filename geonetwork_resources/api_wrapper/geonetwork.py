import requests
from . import config


def get_cookies(client: requests.Session, https_verify: bool=True) -> requests.cookies.RequestsCookieJar:
    """ Connects to the catalog to get session cookies.
    This function is useful to get a CSRF token that can be used in other requests.
    """
    response = client.get(config.api_endpoint, headers={"accept": "application/json"}, verify=https_verify)
    response.raise_for_status()
    return response.cookies or {}


def log_in(user: str, password: str, client: requests.Session=requests.Session()) -> str:
    """ Connect to the catalog and log in with the credentials passed in arguments.
    Returns a tuple2 containing the response object and the cookies generated for this session.
    """
    cookies = get_cookies(client, False)
    token = cookies.get("XSRF-TOKEN", None)

    if not token:
        raise Exception("No XSRF-TOKEN returned.")

    opts = {
        "headers": {
            "accept": "application/json",
            "X-XSRF-TOKEN": token
            },
        "auth": (user, password),
        "cookies": cookies,
        "allow_redirects": True        
    }
    response = client.get(config.api_endpoint, **opts)
    response.raise_for_status()
    return response, cookies
