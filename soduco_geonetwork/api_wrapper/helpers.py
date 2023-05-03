"""
    helpers functions
"""

import csv
import io
import json
import os
import random
import sys
import uuid
import xml.etree.ElementTree as ET
from typing import List
from uuid import UUID


def is_valid_file(parser, arg):
    """
    Test if file exist
    """

    if not os.path.exists(arg):
        parser.error(f"The file {arg} does not exist!")
    else:
        return open(arg, "r", encoding="utf-8")  # return an open file handle


def xml_to_utf8string(xml: ET.ElementTree) -> str:
    """
    Returns the string representation of a ET.ElementTree object encoded in UTF-8
    """
    out = io.BytesIO()
    xml.write(out, xml_declaration=True)
    return out.getvalue().decode("utf-8")


def read_xml_file(file: str) -> str:
    """Read an XML file and returns the section root element"""
    tree = ET.parse(file)

    return tree


def drop_leading_dot_in_xpath(xpath: str) -> str:
    """Function to patch xpaths expressions sent to Geonetwork.

    xml.ElementTree needs Xpaths expressions to start with a dot.
    GeoNetwork needs this dot removed in Xpaths expressions.
    """
    return xpath[1:] if xpath.startswith(".") else xpath


def uuid_list_from_csv(csv_path: str) -> List[UUID]:
    """return uuid list from csv column"""
    if not os.path.exists(csv_path):
        sys.exit("No csv at this path")

    filename = open(csv_path, "r", encoding="utf8")
    file = csv.DictReader(filename)
    uuid_list = []
    for col in file:
        uuid_list.append(col["geonetwork_uuid"])

    return uuid_list


def simulate_upload_json_response() -> json:
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
            f"{db_id}": [
                {
                    "message": f"Metadata imported from XML with UUID {uploaded_record_uuid}",
                    "uuid": uploaded_record_uuid,
                    "draft": "True",
                    "approved": "False",
                    "date": "2022-09-12T15:33:38.417Z",
                }
            ]
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
        "running": "False",
    }

    return response


def get_geonetwork_uuid(json_response: json) -> UUID:
    """Return uuid of uploaded record on Geonetwork from json response"""

    # The key "Id" in "metadaInfos" change for every response, we can't access it directly
    # That's why next(iter(dict)) is needed here.
    database_record_id = next(iter(json_response["metadataInfos"]))
    geonetwork_uuid = json_response["metadataInfos"][database_record_id][0]["uuid"]

    return geonetwork_uuid


def replace_uuid(csv_file: str, output_file: str):
    """Replace yaml identifier by geonerwork uuid"""

    postponed_list = []
    fieldnames = [
        "yaml_identifier",
        "geonetwork_uuid",
        "xml_file_path",
        "postponed_values",
    ]

    with open(csv_file, encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for row in reader:
            postponed_list.append(row)

        for postponed in postponed_list:
            postponed_values = json.loads(postponed["postponed_values"])

            postponed_values["uuid"] = return_uuid(
                postponed_list, postponed_values["uuid"]
            )
            if "associatedResource" in postponed_values.keys():
                for ressource in postponed_values["associatedResource"]:
                    ressource["value"] = return_uuid(postponed_list, ressource["value"])
            if "resourceLineage" in postponed_values.keys():
                for index, ressource in enumerate(postponed_values["resourceLineage"]):
                    postponed_values["resourceLineage"][index] = return_uuid(
                        postponed_list, ressource
                    )
            postponed["postponed_values"] = json.dumps(postponed_values)

    with open(output_file, "w", newline="", encoding="utf8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)

        writer.writeheader()
        for row in postponed_list:
            writer.writerow(row)


# Parcours toute la liste, y a sûrement plus propre comme méthode
def return_uuid(uuid_list: list, identifier: str):
    """
            Take local yaml identifier and
            return corresponding uuid from upload response
    ²"""
    for geonetwork_uuid in uuid_list:
        if geonetwork_uuid["yaml_identifier"] == identifier:
            return geonetwork_uuid["geonetwork_uuid"]


def dump_uploaded_uuid(csv_dump: List[dict], output_file: str):
    """take a list of dictionnaries and dump dict as rows in a csv"""

    field_names = [
        "yaml_identifier",
        "geonetwork_uuid",
        "xml_file_path",
        "postponed_values",
    ]

    with open(output_file, "w", newline="", encoding="utf8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(csv_dump)

    # uuids_output_{time.strftime("%Y%m%d-%H%M%S")}


def read_postponed_values(csv_file: str) -> list:
    """Take a csv in input and return a list of dictionnaries containing records to edit"""
    with open(csv_file, encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)
        postponed_list = []
        for row in reader:
            postponed_list.append(json.loads(row["postponed_values"]))

        return postponed_list
