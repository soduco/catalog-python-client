"""
    Scripts to call batch edit from api
"""

import json
import requests
import login

CATALOG = "https://catalog.geohistoricaldata.org/geonetwork"
API_ROUTE = "/srv/api/records/batchediting"

CATALOGUSER="admin"
CATALOGPASS="admin"

def batch_edit(client: requests.Session, uuid_list: list, xpath: str, value: str, **kwargs):
    """
        Call the batch_edit API endpoint in geonetwork.

        :param requests.Session client: the http connexion
        :param list uuid_list: list of uuid in str format to edit
        :param str xpath: xpath of the element to edit
        :param str value: the xml element to add

        Each xmlns must be declared.
        The body request must look like this example, which add a source dataset:
        "[{
            \"xpath\":\"//mdb:resourceLineage/mrl:LI_Lineage\",
            \"value\":
                \"<mrl:source xmlns:mrl=\\\"http://standards.iso.org/iso/19115/-3/mrl/2.0\\\"
                uuidref=\\\"e34f34cb-240a-469b-95f5-97075490505b\\\"/>\"
        }]"
    """

    client = client or requests.session()

    cookies = kwargs.get("cookies", None)
    if cookies is None:
        _, cookies = login.log_in(client, CATALOGUSER, CATALOGPASS)

    url = CATALOG + API_ROUTE

    headers = {
        "X-XSRF-TOKEN": cookies.get("XSRF-TOKEN"),
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    params = {
        "uuids": uuid_list,
        "updateDateStamp": "true"
    }

    # We drop the . before \\ in xpath
    # It's needed for Etree but not for normal xpath behavior
    if xpath[0] == ".":
        xpath = xpath[1:]

    data = [
                {
                    "xpath":xpath,
                    "value":value
                }
            ]


    response = client.put(url,
                params=params,
                headers=headers,
                cookies=cookies,
                auth=(CATALOGUSER, CATALOGPASS),
                # data needs to be in json format here
                # python string doesnt work
                data=json.dumps(data)
                )
    response.raise_for_status()


    return response.json()
