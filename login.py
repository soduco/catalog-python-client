"""
    Functions to log in the geonetorwk
"""

import requests

CATALOG = "https://catalog.geohistoricaldata.org/geonetwork"
API_ROUTE = "/srv/api/me"

# XSRF-TOKEN seems to be given only on first demand, so we need to store it
def get_cookies(client: requests.Session) -> requests.cookies.RequestsCookieJar:
    """ Connects to the catalog to get session cookies.
    This function is useful to get a CSRF token that can be used in other requests.
    """

    cookie_url = CATALOG + API_ROUTE
    response = client.get(cookie_url, headers={"accept": "application/json"})
    response.raise_for_status()

    return response.cookies or {}


def log_in(client: requests.Session, user: str, password: str) -> str:
    """ Connect to the catalog and log in with the credentials passed in arguments.
    Returns a tuple2 containing the response object and the cookies generated for this session.
    """

    cookies = get_cookies(client)
    token = cookies.get("XSRF-TOKEN", None)

    if not token:
        raise Exception("No XSRF-TOKEN returned.")

    url_userinfo = CATALOG + API_ROUTE
    headers = {
        "accept": "application/json",
        "X-XSRF-TOKEN": token
        }
    auth = (user, password)

    response = client.get(url_userinfo,
                   headers=headers,
                   auth=auth,
                   cookies=cookies,
                   allow_redirects=True)
    response.raise_for_status()

    return response, cookies
