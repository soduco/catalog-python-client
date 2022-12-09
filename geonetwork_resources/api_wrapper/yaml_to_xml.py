import argparse
from helpers import is_valid_file
import yaml
import xml_composers
import xml.etree.ElementTree as ET
import os

def yaml_to_xml():
    """
        Read yaml file
        Build XML record
        Dump result in a xml file
    """

    parser = argparse.ArgumentParser(description='Upload records from a YAML file')
    parser.add_argument("-i", dest="inputfile",
                        required=True,
                        help='input YAML file, with records to upload',
                        metavar="INPUT FILE",
                        type=lambda x: is_valid_file(parser, x))
    
    args = parser.parse_args()

    # Loads a dataset definition from a YAML document
    with args.inputfile as yaml_multidoc:

        yaml_documents = list(yaml.load_all(yaml_multidoc, Loader=yaml.SafeLoader))

        i = 1

        for yaml_doc in yaml_documents:
            builder = xml_composers.IsoDocumentBuilder(yaml_doc)
            xml_tree = builder.compose_xml()
            ET.indent(xml_tree)

            # we strip the input filename of it's path and extension
            # and add a number to form the xml filename
            # ex : fixtures/instance.yaml -> instance_01.xml
            xml_filename = os.path.basename(args.inputfile.name)
            xml_filename = os.path.splitext(args.inputfile.name)[0]
            xml_filename = f"{xml_filename}_{i}.xml"
            xml_tree.write(xml_filename)

            i+=1
