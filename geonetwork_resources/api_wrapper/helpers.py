"""
    helpers functions
"""

import os, io
from typing import Any
import xml.etree.ElementTree as ET


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
    """ET needs Xpaths expressions to start with a dot, but GeoNetwork doesn't behave as expected if there is a leading dot in the Xpath.
    This helper function is used to patch xpaths expressions used to manipualte a ETree that must also be sent to the Geonetwork server. 
    """
    return xpath[1:] if xpath.startswith(".") else xpath