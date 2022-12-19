"""
    helpers functions
"""

import csv
import io
import os
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
        return open(arg, 'r', encoding='utf-8')  # return an open file handle



def xml_to_utf8string(xml: ET.ElementTree) -> str:
    """
        Returns the string representation of a ET.ElementTree object encoded in UTF-8
    """
    out = io.BytesIO()
    xml.write(out, xml_declaration=True)
    return out.getvalue().decode("utf-8")


def drop_leading_dot_in_xpath(xpath: str) -> str:
    """Function to patch xpaths expressions sent to Geonetwork.

    xml.ElementTree needs Xpaths expressions to start with a dot.
    GeoNetwork needs this dot removed in Xpaths expressions.
    """
    return xpath[1:] if xpath.startswith(".") else xpath


def uuid_list_from_csv(csv_path: str) -> List[UUID]:
    """return uuid list from csv column
    """
    if not os.path.exists(csv_path):
        return
    else:
        filename = open(csv_path, 'r', encoding='utf8')
        # creating dictreader object
        file = csv.DictReader(filename)
        # creating empty lists
        uuid_list = []
        # iterating over each row and append
        # values to empty list
        for col in file:
            uuid_list.append(col['uuid'])

        return uuid_list
