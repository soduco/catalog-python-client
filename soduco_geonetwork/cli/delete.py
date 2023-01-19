"""CLI module to call delete function from dataset module
"""

import click
from soduco_geonetwork.api_wrapper import (config, dataset, geonetwork,
                                              helpers)


@click.command()
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
