"""script to test upload and edit function"""

import csv
import os
import time
import xml.etree.ElementTree as ET

import requests
import yaml
from geonetwork_resources.api_wrapper import (config, dataset, geonetwork,
                                              xml_composers, helpers)

__location__ = os.path.realpath(
os.path.join(os.getcwd(), os.path.dirname(__file__)))

def main():
    """
        Read fixtures/instance.yaml
        Build XML records
        Upload them on catalog
    """

    session = geonetwork.log_in(config.config['GEONETWORK_USER'],
                                config.config['GEONETWORK_PASSWORD'])

    # Loads a dataset definition from a YAML document
    with open(f'{__location__}/fixtures/instance.yaml', encoding='utf8') as yaml_multidoc:

        uuid_list, postponed_list = [], []
        yaml_documents = list(yaml.load_all(yaml_multidoc, Loader=yaml.SafeLoader))


        for yaml_doc in yaml_documents:
            builder = xml_composers.IsoDocumentBuilder(yaml_doc)
            xml_tree = builder.compose_xml()

            # Beautify XML doc
            ET.indent(xml_tree)

            # json_response = dataset.upload(xml_tree, session).json()
            json_response = helpers.simulate_upload_json_response()


            if json_response['errors'] is None:
                print(json_response['errors'])
            else:
                print(json_response['metadataInfos'])

            # See fictures/upload_json_response.json to see json response fixtures

            # The key "Id" in "metadaInfos" change for every response, we can't access it directly
            # That's why next(iter(dict)) is needed here.
            database_record_id = next(iter(json_response['metadataInfos']))
            _uuid = json_response['metadataInfos'][database_record_id][0]['uuid']

            dict_to_append = {'local_id': yaml_doc['identifier'], 'uuid': _uuid}
            uuid_list.append(dict_to_append)
            postponed_list.append(builder.postponed)

        dump_uploaded_uuid(uuid_list, filepath=f'{__location__}/fixtures/test_uuids.csv')

        replace_uuid(uuid_list, postponed_list)

        edit_postponed_values(session, postponed_list)



#region EDIT

def edit_postponed_values(session: requests.Session, postponed_list: list):
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
            if postponed['associatedResource']:
                for associated_ressource in postponed['associatedResource']:
                    builder = xml_composers.AssociatedRessource(
                        value=associated_ressource['value'],
                        typeOfAssociation=associated_ressource['typeOfAssociation']
                    )
                    xml_element = ET.tostring(builder.compose_xml(), encoding='unicode')
                    for namespace, uri in xml_composers.PREFIX_MAP.items():
                        ET.register_namespace(namespace, uri)
                    dataset.update([postponed['uuid']],
                                   builder.parent_element_xpath,
                                   xml_element,
                                   session)

            if postponed['resourceLineage']:
                for _uuid in postponed['resourceLineage']:
                    builder = xml_composers.ResourceLineage(uuidref=_uuid)
                    xml_element = ET.tostring(builder.compose_xml(), encoding='unicode')
                    for namespace, uri in xml_composers.PREFIX_MAP.items():
                        ET.register_namespace(namespace, uri)
                    dataset.update([postponed['uuid']],
                                   builder.parent_element_xpath,
                                   xml_element,
                                   session)


#region HELPERS

# take all uuids at once
def dump_uploaded_uuid(uuid_list: list, filepath: str):
    """
        dump an uuid list from uploaded records
        in a file with a timestamp
    """

    fields = ['yaml_identifier', 'uuid']

    rows = []

    for _uuid in uuid_list:
        rows.append([_uuid['local_id'], _uuid['uuid']])


    if filepath is None:
        filepath = f'{__location__}/uuids_output_{time.strftime("%Y%m%d-%H%M%S")}.csv'

    with open(filepath, 'w', encoding='utf8') as file:
        # using csv.writer method from CSV package
        write = csv.writer(file)
        write.writerow(fields)
        write.writerows(rows)

#endregion


# On remplace "l'identifier" du yaml par l'uuid récupéré à l'upload
def replace_uuid(uuid_list: list, postponed_list: list):
    """
    postponed_list structure example:
    [
        defaultdict(<class 'list'>, {
            'uuid': '004',
            'associatedResource': [
                {
                    'value': '002',
                    'typeOfAssociation': 'largerWorkCitation'
                },
                {
                    'value': '003',
                    'typeOfAssociation': 'largerWorkCitation'
                }
            ],
            'resourceLineage': [
                '001'
                ]
            })
        ]
    """

    # print(uuid_list)
    # print(postponed_list)

    for postponed in postponed_list:
        postponed['uuid'] = return_uuid(uuid_list, postponed['uuid'])
        if 'associatedResource' in postponed:
            for ressource in postponed['associatedResource']:
                ressource['value'] = return_uuid(uuid_list, ressource['value'])
        if 'resourceLineage' in postponed:
            for index, ressource in enumerate(postponed['resourceLineage']):
                postponed['resourceLineage'][index] = return_uuid(uuid_list, ressource)

#endregion


# Parcours toute la liste, y a sûrement plus propre comme méthode
def return_uuid(uuid_list: list, identifier: str):
    """
        Take local yaml identifier and
        return corresponding uuid from upload response
    """
    print(uuid_list)
    for _uuid in uuid_list:
        if _uuid['local_id'] == identifier:
            return _uuid['uuid']


#region main entrypoint
if __name__ == "__main__":
    main()
#endregion
