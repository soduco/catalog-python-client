"""script to test delete function"""

import csv
import os

import requests
from geonetwork_resources.api_wrapper import (config, dataset, geonetwork,
                                              helpers)

__location__ = os.path.realpath(
os.path.join(os.getcwd(), os.path.dirname(__file__)))

#region DELETE

def main():
    """
        Read fixtures/test_uuids.csv (if it exists)
        delete records from uuid
    """

    session = geonetwork.log_in(config.config["GEONETWORK_USER"],
                                config.config["GEONETWORK_PASSWORD"])

    uuid_list = helpers.uuid_list_from_csv(f'{__location__}/fixtures/generated/test2.csv')

    if not uuid_list:
        print("The file fixtures/generated/test2.csv does not exist!")
    else:
        response = dataset.delete(uuid_list, session=session)
        print(response)

#end region


def delete_records_from_csv(session: requests.Session, csv_file: str) -> list:
    """
        Delete one or more records by their uuid from a csv file

        CSV format:
        yaml_identifier,uuid
    """
    uuid_list = []
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            uuid_list.append(row["geonework_uuid"])
    response = dataset.delete(uuid_list,session=session)

    print(response)


#endregion

#region main entrypoint
if __name__ == "__main__":
    main()
#endregion
