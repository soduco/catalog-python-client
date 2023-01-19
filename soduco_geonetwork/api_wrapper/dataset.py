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
           session: requests.Session=requests.session(),
           backup_records: bool=True):
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

    for namespace, uri in xml_composers.PREFIX_MAP.items():
        ET.register_namespace(namespace, uri)
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


def edit_postponed_values(postponed_values: dict, session: requests.Session=requests.Session()):
    """Edit the postponed links between recently uploaded records
    """

    geonetwork_uuid = postponed_values['uuid']

    if 'associatedResource' in postponed_values.keys():
        for associated_ressource in postponed_values['associatedResource']:
            builder = xml_composers.AssociatedRessource(
                value=associated_ressource['value'],
                typeOfAssociation=associated_ressource['typeOfAssociation']
            )
            for namespace, uri in xml_composers.PREFIX_MAP.items():
                ET.register_namespace(namespace, uri)
            xml_element = ET.tostring(builder.compose_xml(), encoding='unicode')
            update([geonetwork_uuid],
                    builder.parent_element_xpath,
                    xml_element,
                    session)

    if 'resourceLineage' in postponed_values.keys():
        for resource in postponed_values['resourceLineage']:
            builder = xml_composers.ResourceLineage(uuidref=resource)
            for namespace, uri in xml_composers.PREFIX_MAP.items():
                ET.register_namespace(namespace, uri)
            xml_element = ET.tostring(builder.compose_xml(), encoding='unicode')
            update([geonetwork_uuid],
                    builder.parent_element_xpath,
                    xml_element,
                    session)

# endregion
