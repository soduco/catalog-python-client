"""CLI module to call parse function from yaml_to_xml module
"""

import click
from geonetwork_resources.api_wrapper import yaml_to_xml


@click.command()
@click.argument('input_yaml_file', type=click.Path(exists=True))
@click.argument('output_folder', type=click.Path(exists=True))

def parse(input_yaml_file, output_folder):
    """
    Needs 2 arguments:

    - A yaml file with one or more documents to parse to xml

    - A folder to save the xml files generated and a csv with info on files generated
    """
    yaml_to_xml.parse(input_yaml_file, output_folder)
