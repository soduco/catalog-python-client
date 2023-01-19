"""CLI module to call upload function
"""

import csv
import os
import xml.etree.ElementTree as ET

import click
from soduco_geonetwork.api_wrapper import (config, dataset, geonetwork,
                                              helpers, xml_composers)


@click.command()
@click.argument('csv_file', type=click.Path(exists=True))


def upload(csv_file):
    """
    Needs 1 arguments:

    - A csv file with info of the xml files to upload
    """
    session = geonetwork.log_in(config.config['GEONETWORK_USER'],
                                config.config['GEONETWORK_PASSWORD'])

    file = open(csv_file, 'r', encoding='utf8')
    reader = csv.DictReader(file)

    dirname = os.path.dirname(csv_file)
    temp_file = f"{dirname}/temp.csv"
    rows_to_dump = []

    for row in reader:
        # xml_file = helpers.xml_to_utf8string((helpers.read_xml_file(f"{dirname}/{row['xml_file']}")))
        xml_file = helpers.read_xml_file(f"{dirname}/{row['xml_file']}")
        json_response = dataset.upload(xml_file, session).json()
        geonetwork_uuid = helpers.get_geonetwork_uuid(json_response)
        row['geonetwork_uuid'] = geonetwork_uuid
        rows_to_dump.append(row)

        print(json_response)

    helpers.dump_uploaded_uuid(rows_to_dump, temp_file)
    helpers.replace_uuid(temp_file, csv_file)
