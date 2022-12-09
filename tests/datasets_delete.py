import argparse
import requests
from geonetwork_resources.api_wrapper import geonetwork, config, helpers, dataset
import csv

#region DELETE

def main():
    """
        read arguments to choose wich script to execute
    """
    parser = argparse.ArgumentParser(description='Upload records from a YAML file')
    parser.add_argument("-i", dest="inputfile",
                        help='delete records from a csv file, with uuid(s) to delete on second column',
                        metavar="INPUT FILE",
                        type=lambda x: helpers.is_valid_file(parser, x))
    parser.add_argument("-l", dest="uuidList",
                        default=None,
                        help='delete records from a uuid list, in string format and separated by comma',
                        metavar="UUID LIST")

    args = parser.parse_args()

    if not (args.inputfile or args.uuidList):
        parser.error('No action requested, add -i or -l')

    session = geonetwork.log_in(config.config["GEONETWORK_USER"], config.config["GEONETWORK_PASSWORD"])
    
    if args.inputfile:
        delete_records_from_csv(session=session, csv_file=args.inputfile.name)
    if args.uuidList:
        dataset.delete(args.uuidList, session=session)

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
            uuid_list.append(row["uuid"])
    dataset.delete(uuid_list,session=session)

#endregion

#region main entrypoint
if __name__ == "__main__":
    main()
#endregion
