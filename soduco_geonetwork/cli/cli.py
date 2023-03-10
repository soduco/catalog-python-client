"""CLI module to call delete function from dataset module
"""

import csv
import os
import tempfile

import click
from soduco_geonetwork.api_wrapper import (config, dataset, geonetwork,
                                           helpers, yaml_to_xml)


@click.group()
def cli():
    """Main function
    """
    values_that_must_be_present = ["GEONETWORK", "API_PATH",
                                   "GEONETWORK_USER", "GEONETWORK_PASSWORD"]

    for value in values_that_must_be_present:
        if (value in config.config and config.config[value] is not None):
            pass
        else:
            raise AssertionError("Environment value SECRET not set.")

@cli.command()
@click.argument('input_yaml_file', type=click.Path(exists=True))
@click.option('--output_folder')
def parse(input_yaml_file, output_folder):
    """
    Needs 1 arguments:

    - A yaml file with one or more documents to parse to xml (dumped in tmp folder by default)
    """

    if not input_yaml_file.endswith(('.yml', '.yaml')):
        raise ValueError("Not a yaml file")

    if output_folder is None:
        output_folder = tempfile.mkdtemp()
        print('folder ' + output_folder + ' created. Parsing YAML file.')
    else:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print('folder ' + output_folder + ' created. Parsing YAML file.')
        else:
            print('folder ' + output_folder + ' already present. Parsing YAML file.')

    yaml_to_xml.parse(input_yaml_file, output_folder)

    print('yaml_list dumped in current folder : ' + os.getcwd())

@cli.command()
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


@cli.command()
@click.argument('input_csv_file', type=click.Path(exists=True))
@click.argument('edition_location', type=str)
@click.argument('xml_patch', type=str)
def update(input_csv_file, edition_location, xml_patch):
    """
    Needs 3 arguments:

    - A csv file with a column "geonetwork_uuid" with uuids to delete

    - An edition location in the document (in Xpath)

    - A xml element to save at the location (it will erase any previous element)
    """

    session = geonetwork.log_in(config.config['GEONETWORK_USER'],
                                config.config['GEONETWORK_PASSWORD'])

    uuid_list = helpers.uuid_list_from_csv(input_csv_file)

    response = dataset.update(uuid_list, edition_location, xml_patch, session)
    print(response)


@cli.command()
@click.argument('csv_postponed_values', type=click.Path(exists=True))
def update_postponed_values(csv_postponed_values):
    """Edit the postponed links between uploaded records

    Needs a csv file with postponed values
    (generated by parse command and updated at upload with geonetwork uuid)
    """

    session = geonetwork.log_in(config.config['GEONETWORK_USER'],
                                config.config['GEONETWORK_PASSWORD'])

    postponed_list = helpers.read_postponed_values(csv_postponed_values)

    for item in postponed_list:
        dataset.edit_postponed_values(item, session)


@cli.command()
@click.argument('input_csv_file', type=click.Path(exists=True))
def delete(input_csv_file):
    """
    Needs 1 argument:

    - A csv file with a column "geonetwork_uuid" with uuids to delete
    """

    session = geonetwork.log_in(config.config['GEONETWORK_USER'],
                                config.config['GEONETWORK_PASSWORD'])

    uuid_list = helpers.uuid_list_from_csv(input_csv_file)

    response = dataset.delete(uuid_list, session).json()

    print(response)

if __name__ == '__main__':
    cli()
