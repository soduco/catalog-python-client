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

    # WIP
    # Must then call other functions to delete files

#region main entrypoint
if __name__ == "__main__":
    main()
#endregion
