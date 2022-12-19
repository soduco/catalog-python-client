"""Log in functions
"""

import requests
from . import config

def get_cookies(session: requests.Session,
                https_verify: bool=True) -> requests.cookies.RequestsCookieJar:
    """ Connect to Geonetwork API and return the cookies for the session passed is parameters.
    This function is useful to get a CSRF token that can be used in other requests.
    """
    headers={"accept": "application/json"}
    response = session.get(config.api_route_me, headers=headers, verify=https_verify)
    response.raise_for_status()
    return response.cookies or {}


def log_in(user: str, password: str, session: requests.Session=requests.Session()) -> str:
    """ Connect to Geonetwork using the username and password in parameters.
    Returns a requests.Session with a cookie holding a CSRF_TOKEN.
    """
    cookies = get_cookies(session)
    token = cookies.get("XSRF-TOKEN", None)

    if not token:
        raise Exception("Could not get a XSRF-TOKEN.")

    opts = {
        "headers": {
            "accept": "application/json",
            "X-XSRF-TOKEN": token
            },
        "auth": (user, password),
        "cookies": cookies,
        "allow_redirects": True        
    }
    response = session.get(config.api_route_me, **opts)
    response.raise_for_status()

    # Update session cookies with the cookie holding the CSRF TOKEN
    cookies = requests.utils.dict_from_cookiejar(response.cookies)
    session.cookies.update(cookies)
    return session
