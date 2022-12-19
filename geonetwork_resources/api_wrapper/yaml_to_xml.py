"""Script that build xml records from yaml documents
"""

import os
import xml.etree.ElementTree as ET
import csv
import time
import yaml
from . import xml_composers


def yaml_to_xml(inputfile: str, outpufolder: str):
    """
        Read yaml file -> Build XML record
        Dump result in a xml file with "xml.etree.ElementTree.write()"
        Dump csv with yaml identifiers and corresponding xml file
    """

    # Loads a dataset definition from a YAML document
    with open(inputfile, encoding='utf8') as yaml_multidoc:

        doc_infos = []

        yaml_documents = list(yaml.load_all(yaml_multidoc, Loader=yaml.SafeLoader))

        for yaml_doc in yaml_documents:

            
            builder = xml_composers.IsoDocumentBuilder(yaml_doc)
            xml_tree = builder.compose_xml()
            ET.indent(xml_tree) # Beautify XML doc

            # we strip the input filename of it's path and extension
            # and add a number to form the xml filename
            # ex : fixtures/instance.yaml -> instance_01.xml
            xml_filename = os.path.basename(inputfile)
            xml_filename = os.path.splitext(inputfile)[0]
            xml_filename = f"{yaml_doc['identifier']}.xml"
            xml_tree.write(xml_filename)

            doc_infos.append({"identifier": yaml_doc["identifier"], "xml_file": xml_filename})

    fields = ['yaml_identifier', 'xml_file']

    rows = []

    for info in doc_infos:
        rows.append([info['identifier'], info['xml_file']])

        outpufile = f'{outpufolder}/uuids_output_{time.strftime("%Y%m%d-%H%M%S")}.csv'

    with open(outpufile, 'w', encoding='utf8') as file:
        # using csv.writer method from CSV package
        write = csv.writer(file)
        write.writerow(fields)
        write.writerows(rows)
