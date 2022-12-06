from typing import List
import xml.etree.ElementTree as ET
import requests
from . import config
from uuid import UUID
from . import helpers
import json

#region DELETE
 
def delete(uuid_list: List[UUID], backup_records: bool=True, session: requests.Session=requests.session()):
    """ delete one or more records from their uuid """
    # TODO : ensure that the session is "logged in" ?
    token = session.cookies.get_dict().get("XSRF-TOKEN")
    headers = {
        "X-XSRF-TOKEN": token,
        "accept": "application/json"
    }
    params = {
        "uuids": uuid_list,
        "withBackup": backup_records
    }
    
    response = session.delete(config.api_route_records, headers=headers, params=params)
    response.raise_for_status()
    return response

#endregion

# region UPLOAD

def upload(xml: ET.ElementTree, session: requests.Session=requests.Session()):
    """ Upload a xml metadata file in the catalog and return its UUID """
    # TODO : ensure that the session is "logged in" ?
    token = session.cookies.get_dict().get("XSRF-TOKEN")
    
    xml_string = helpers.xml_to_utf8string(xml)
    headers= {
        "X-XSRF-TOKEN": token,
        "accept": "application/json",
        "Content-Type": "application/xml",
    }
    payload = xml_string
    response = session.put(config.api_route_records, headers=headers, data=payload)
    response.raise_for_status()
    return response

# endregion

# region UPDATE

def update(uuid_list: List[UUID], edition_location: str, xml_patch: str, session: requests.Session=requests.Session()):
    xpath = helpers.drop_leading_dot_in_xpath(edition_location)    
    payload = json.dumps([{"xpath":xpath, "value": xml_patch}])
    
    token = session.cookies.get_dict().get("XSRF-TOKEN")
    headers = {
        "X-XSRF-TOKEN": token,
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    
    params = {
        "uuids": uuid_list,
        "updateDateStamp": True
    }
    
    response = session.put(config.api_route_batchediting, headers=headers, params=params, data=payload)
    response.raise_for_status()
    return response.json()

# endregion
