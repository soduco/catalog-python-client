"""
    This scripts delete one or multiple records
    based on their uuid
"""

import argparse
import csv
import requests
import login
from _helpers import is_valid_file


CATALOG = "https://catalog.geohistoricaldata.org/geonetwork"
api_routes = {
    "records": "/srv/api/records",
}

CATALOGUSER="admin"
CATALOGPASS="admin"
FUNCTION_LIST = ['del', 'del_csv']

#region DELETE

def main():
    """
        read arguments to choose wich script to execute
    """
    parser = argparse.ArgumentParser(description='Upload records from a YAML file')
    parser.add_argument("-i", dest="inputfile",
                        help='delete records from a csv file, with uuid(s) to delete on second column',
                        metavar="INPUT FILE",
                        type=lambda x: is_valid_file(parser, x))
    parser.add_argument("-l", dest="uuidList",
                        default=None,
                        help='delete records from a uuid list, in string format and separated by comma',
                        metavar="UUID LIST")

    args = parser.parse_args()

    if not (args.inputfile or args.uuidList):
        parser.error('No action requested, add -i or -l')

    client = requests.Session()
    _, cookies = login.log_in(client, CATALOGUSER, CATALOGPASS)

    if args.inputfile:
        delete_records_from_csv(client=client, csv_file=args.inputfile.name, cookies=cookies)
    if args.uuidList:
        delete_records(
            client=client,
            uuid_list=args.uuidList,
            backup_records="true",
            cookies=cookies)

#end region


#region DELETE

def delete_records(client: requests.Session, uuid_list: list, backup_records: str, **kwargs):
    """ delete one or more records from their uuid """

    client = client or requests.session()
    cookies = kwargs.get("cookies", None)
    if cookies is None:
        _, cookies = login.log_in(client, CATALOGUSER, CATALOGPASS)

    url = CATALOG + api_routes.get("records") + "?uuids=" + uuid_list[0]

    for _uuid in uuid_list[1:]:
        url += f"&uuids={_uuid}"

    url += f"&withBackup={backup_records}"

    headers = {
        "X-XSRF-TOKEN": cookies.get("XSRF-TOKEN"),
        "accept": "application/json"
    }

    response = client.delete(url,
                    auth=(CATALOGUSER, CATALOGPASS),
                    headers=headers)
    response.raise_for_status()

    return response.json()

def delete_records_from_csv(client: requests.Session, csv_file: str, **kwargs) -> list:
    """
        Delete one or more records by their uuid from a csv file

        CSV format:
        yaml_identifier,uuid
    """

    client = client or requests.session()
    cookies = kwargs.get("cookies", None)
    if cookies is None:
        _, cookies = login.log_in(client, CATALOGUSER, CATALOGPASS)

    uuid_list = []
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            uuid_list.append(row["uuid"])

    delete_records(client=client, uuid_list=uuid_list, backup_records="true", cookies=cookies)

#endregion

#region main entrypoint
if __name__ == "__main__":
    main()
#endregion
