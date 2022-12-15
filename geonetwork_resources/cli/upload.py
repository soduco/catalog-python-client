import argparse
from geonetwork_resources.api_wrapper import geonetwork, config, helpers, dataset

def main():
    parser = argparse.ArgumentParser(description='Upload records from a YAML file')
    parser.add_argument("-i", dest="inputfile",
                        required=True,
                        help='input YAML file, with records to upload',
                        metavar="INPUT FILE",
                        type=lambda x: helpers.is_valid_file(parser, x))
    parser.add_argument("-o", dest="dumpfile",
                        default=None,
                        help='dump file for uuids generated',
                        metavar="OUTPUT FILE")

    args = parser.parse_args()

    print(args)

    # WIP
    # Must then call other functions to upload files

#region main entrypoint
if __name__ == "__main__":
    main()
#endregion
