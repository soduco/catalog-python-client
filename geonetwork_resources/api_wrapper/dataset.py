"""This module contains methods to interact with records on geonetwork via its API

    You can :
    - upload
    - edit
    - delete
"""

import json
import xml.etree.ElementTree as ET
from typing import List
from uuid import UUID

import requests

from . import config, helpers, xml_composers

#region DELETE

def delete(uuid_list: List[UUID],
           backup_records: bool=True,
           session: requests.Session=requests.session()):
    """ delete one or more records from their uuid """
    # TODO : ensure that the session is "logged in" ?
    token = session.cookies.get_dict().get('XSRF-TOKEN')
    headers = {
        'X-XSRF-TOKEN': token,
        'accept': 'application/json'
    }
    params = {
        'uuids': uuid_list,
        'withBackup': backup_records
    }

    response = session.delete(config.api_route_records, headers=headers, params=params)
    response.raise_for_status()
    return response

#endregion

# region UPLOAD

def upload(xml: ET.ElementTree, session: requests.Session=requests.Session()):
    """ Upload a xml metadata file in the catalog and return its UUID """
    # TODO : ensure that the session is "logged in" ?
    token = session.cookies.get_dict().get('XSRF-TOKEN')

    xml_string = helpers.xml_to_utf8string(xml)
    headers= {
        'X-XSRF-TOKEN': token,
        'accept': 'application/json',
        'Content-Type': 'application/xml',
    }
    payload = xml_string
    response = session.put(config.api_route_records, headers=headers, data=payload)
    response.raise_for_status()
    return response

# endregion

# region UPDATE

def update(uuid_list: List[UUID],
           edition_location: str,
           xml_patch: str,
           session: requests.Session=requests.Session()):
    """
    Call the batch_edit API endpoint in geonetwork.

    :param session requests.Session: the http connexion
    :param List[UUID] uuid_list: list of uuid to edit
    :param str edition_location: xpath of the element to edit
    :param str xml_patch: the xml element to add

    Each xmlns must be declared.
    The body request must look like this example, which add a source dataset:
    "[{
        \"xpath\":\"//mdb:resourceLineage/mrl:LI_Lineage\",
        \"value\":
            \"<mrl:source xmlns:mrl=\\\"http://standards.iso.org/iso/19115/-3/mrl/2.0\\\"
            uuidref=\\\"e34f34cb-240a-469b-95f5-97075490505b\\\"/>\"
    }]"
    """

    xpath = helpers.drop_leading_dot_in_xpath(edition_location)
    payload = json.dumps([{'xpath':xpath, 'value': xml_patch}])

    token = session.cookies.get_dict().get('XSRF-TOKEN')
    headers = {
        'X-XSRF-TOKEN': token,
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    params = {
        'uuids': uuid_list,
        'updateDateStamp': True
    }

    response = session.put(config.api_route_batchediting,
                           headers=headers,
                           params=params,
                           data=payload)
    response.raise_for_status()
    return response


def edit_postponed_values(postponed_list: list, session: requests.Session=requests.Session()):
    """
        Edit the postponed links between recently uploaded records
        Each item in postponed_list contain its uuid, so:
        if len(item) in postponed_list > 1:
            there is something to edit
    """
    # TO REFACTOR
    # We will edit each value separately for now
    # but with "batch edit" API we could eventually edit all same values at once
    # like if every instance have the "001" yaml document as a resource Lineage
    for postponed in postponed_list:
    # if element lenght = 1 it contains only its uuid
        if len(postponed) > 1:
            if 'associatedResource' in postponed.keys():
                for associated_ressource in postponed['associatedResource']:
                    builder = xml_composers.AssociatedRessource(
                        value=associated_ressource['value'],
                        typeOfAssociation=associated_ressource['typeOfAssociation']
                    )
                    xml_element = ET.tostring(builder.compose_xml(), encoding='unicode')
                    for namespace, uri in xml_composers.PREFIX_MAP.items():
                        ET.register_namespace(namespace, uri)
                    update([postponed['uuid']],
                            builder.parent_element_xpath,
                            xml_element,
                            session)

            if 'resourceLineage' in postponed.keys():
                for resource in postponed['resourceLineage']:
                    builder = xml_composers.ResourceLineage(uuidref=resource)
                    xml_element = ET.tostring(builder.compose_xml(), encoding='unicode')
                    for namespace, uri in xml_composers.PREFIX_MAP.items():
                        ET.register_namespace(namespace, uri)
                    update([postponed['uuid']],
                            builder.parent_element_xpath,
                            xml_element,
                            session)

# endregion
