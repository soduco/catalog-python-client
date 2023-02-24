"""Script that build xml records from yaml documents
"""

import csv
import json
import os
import xml.etree.ElementTree as ET

import yaml

from . import xml_composers


def parse(input_file: str, output_folder: str):
    """
        Read yaml file -> Build XML record with xml_composers
        Dump result in a xml file with "xml.etree.ElementTree.write()"
        Dump csv with yaml identifiers, corresponding xml file and postponed values
    """

    # Loads a dataset definition from a YAML document
    with open(input_file, encoding='utf8') as yaml_multidoc:

        doc_infos = []

        yaml_documents = list(yaml.load_all(yaml_multidoc, Loader=yaml.SafeLoader))

        for yaml_doc in yaml_documents:
            builder = xml_composers.IsoDocumentBuilder(yaml_doc)
            xml_tree = builder.compose_xml()
            ET.indent(xml_tree) # Beautify XML doc

            xml_file_path = f"{output_folder}/{yaml_doc['identifier']}.xml"
            xml_tree.write(xml_file_path)

            doc_infos.append({'identifier': yaml_doc['identifier'],
                              'xml_file_path': xml_file_path,
                              'postponed_values': builder.postponed})

    fields = ['yaml_identifier', 'xml_file_path', 'postponed_values']

    rows = []

    # We dump the yaml list in the current folder
    for info in doc_infos:
        rows.append([info['identifier'], info['xml_file_path'], json.dumps(info['postponed_values'])])
        output_file = f'{os.getcwd()}/yaml_list.csv'

    with open(output_file, 'w', newline='', encoding='utf8') as file:
        # using csv.writer method from CSV package
        write = csv.writer(file)
        write.writerow(fields)
        write.writerows(rows)
