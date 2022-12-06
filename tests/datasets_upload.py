import argparse
import yaml
import requests
import xml.etree.ElementTree as ET
from geonetwork_resources.api_wrapper import geonetwork,config, helpers, xml_composers, dataset
import time
import pandas
import uuid
import random

def main():
    """
        Read yaml file
        Build XML record
        We login here to avoid multiple logins, which cause a bug
        XSRF-TOKEN is delivered only on first cookie call
        So, we pass cookies to functions (thus **kwargs argument)
    """

    parser = argparse.ArgumentParser(description='Upload records from a YAML file')
    parser.add_argument("-i", dest="inputfile",
                        required=True,
                        help='input YAML file, with records to upload',
                        metavar="INPUT FILE",
                        type=lambda x: helpers.is_valid_file(parser, x))
    parser.add_argument("-o", dest="dumpfile",
                        default=None,
                        help='dump file for uuids generated',
                        metavar="OUTPUT FILE")

    args = parser.parse_args()

    # Loads a dataset definition from a YAML document
    with args.inputfile as yaml_multidoc:

        uuid_list, postponed_list = [], []
        yaml_documents = list(yaml.load_all(yaml_multidoc, Loader=yaml.SafeLoader))

        session = geonetwork.log_in(config.config["GEONETWORK_USER"], config.config["GEONETWORK_PASSWORD"])

        for yaml_doc in yaml_documents:
            builder = xml_composers.IsoDocumentBuilder(yaml_doc)
            xml_tree = builder.compose_xml()

            # Beautify XML doc
            ET.indent(xml_tree)
            
            json_response = dataset.upload(xml_tree, session).json()

            # See fictures/upload_json_response.json to see json response fixtures

            # The key "Id" in "metadaInfos" change for every response, we can't access it directly
            # That's why next(iter(dict)) is needed here.
            database_record_id = next(iter(json_response["metadataInfos"]))
            _uuid = json_response["metadataInfos"][database_record_id][0]["uuid"]

            dict_to_append = {"local_id": yaml_doc["identifier"], "uuid": _uuid}
            uuid_list.append(dict_to_append)
            postponed_list.append(builder.postponed)

        dump_uploaded_uuid(uuid_list, filepath=args.dumpfile)

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
            if postponed["associatedResource"]:
                for associated_ressource in postponed["associatedResource"]:
                    builder = xml_composers.AssociatedRessource(
                        value=associated_ressource["value"],
                        typeOfAssociation=associated_ressource["typeOfAssociation"]
                    )
                    xml_element = ET.tostring(builder.compose_xml(), encoding="unicode")
                    for namespace, uri in xml_composers.PREFIX_MAP.items():
                        ET.register_namespace(namespace, uri)
                    dataset.update([postponed["uuid"]],
                                   builder.parent_element_xpath,
                                   xml_element,
                                   session)
                    
            if postponed["resourceLineage"]:
                for _uuid in postponed["resourceLineage"]:
                    builder = xml_composers.ResourceLineage(uuidref=_uuid)
                    xml_element = ET.tostring(builder.compose_xml(), encoding="unicode")
                    for namespace, uri in xml_composers.PREFIX_MAP.items():
                        ET.register_namespace(namespace, uri)
                    dataset.update([postponed["uuid"]],
                                   builder.parent_element_xpath,
                                   xml_element,
                                   session)
                   


#region HELPERS

def simulate_upload_json_response():
    """
        helper to simulate upload json response
    """
    response_uuid = str(uuid.uuid4())
    uploaded_record_uuid = str(uuid.uuid4())
    db_id = random.randrange(999)

    response = {
        "errors": [],
        "infos": [],
        "uuid": response_uuid,
        "metadata": [],
        "metadataErrors": {},
        "metadataInfos": {
            f"{db_id}": [{
            "message": f"Metadata imported from XML with UUID {uploaded_record_uuid}",
            "uuid": uploaded_record_uuid,
            "draft": "True",
            "approved": "False",
            "date": "2022-09-12T15:33:38.417Z"
            }]
            },
        "numberOfNullRecords": 0,
        "numberOfRecordsProcessed": 1,
        "numberOfRecordsWithErrors": 0,
        "numberOfRecordNotFound": 0,
        "numberOfRecordsNotEditable": 0,
        "numberOfRecords": 0,
        "startIsoDateTime": "2022-09-12T15:33:38.316Z",
        "endIsoDateTime": "2022-09-12T15:33:38.419Z",
        "ellapsedTimeInSeconds": 0,
        "totalTimeInSeconds": 0,
        "type": "SimpleMetadataProcessingReport",
        "running": "False"
    }

    return response


# take all uuids at once
def dump_uploaded_uuid(uuid_list: list, filepath: str):
    """
        dump an uuid list from uploaded records
        in a file with a timestamp
    """

    local_id_list = []
    uploaded_uuid_list = []

    for _uuid in uuid_list:
        local_id_list.append(_uuid["local_id"])
        uploaded_uuid_list.append(_uuid["uuid"])

    _dict = {'yaml_identifier': local_id_list,'uuid': uploaded_uuid_list}

    if filepath is None:
        filepath = f'uuids_output_{time.strftime("%Y%m%d-%H%M%S")}.csv'

    # csv.writer doesn't works with uuid list
    dataframe = pandas.DataFrame(_dict)
    dataframe.to_csv(filepath, header=True, index=False)
    dataframe.to_csv()

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

    for postponed in postponed_list:
        postponed["uuid"] = return_uuid(uuid_list, postponed["uuid"])
        if "associatedResource" in postponed:
            for ressource in postponed["associatedResource"]:
                ressource["value"] = return_uuid(uuid_list, ressource["value"])
        if "resourceLineage" in postponed:
            for index, ressource in enumerate(postponed["resourceLineage"]):
                postponed["resourceLineage"][index] = return_uuid(uuid_list, ressource)

#endregion


# Parcours toute la liste, y a sûrement plus propre comme méthode
def return_uuid(uuid_list: list, identifier: str):
    """
        Take local yaml identifier and
        return corresponding uuid from upload response
²    """
    for _uuid in uuid_list:
        if _uuid["local_id"] == identifier:
            return _uuid["uuid"]


#region main entrypoint
if __name__ == "__main__":
    main()
#endregion
