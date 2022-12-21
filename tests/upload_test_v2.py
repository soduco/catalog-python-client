"""script to test upload and edit function"""

import os
import csv

from geonetwork_resources.api_wrapper import (config, dataset, geonetwork,
                                              yaml_to_xml, helpers)

__location__ = os.path.realpath(
os.path.join(os.getcwd(), os.path.dirname(__file__)))

def main():
    """
        Read fixtures/instance.yaml
        Build XML records
        Upload them on catalog
    """

    session = geonetwork.log_in(config.config['GEONETWORK_USER'],
                                config.config['GEONETWORK_PASSWORD'])

    yaml_to_xml.yaml_to_xml(inputfile=f"{__location__}/fixtures/instance.yaml",
                            outpufolder=f"{__location__}/fixtures/generated")

    _dir = f"{__location__}/fixtures/generated"

    rows_to_dump = []

    filepath = os.path.join(f"{__location__}/fixtures/generated/yaml_list.csv")

    file = open(filepath, 'r', encoding='utf8')
    reader = csv.DictReader(file)
    for row in reader:
        xml_file = helpers.read_xml_file(f"{__location__}/fixtures/generated/{row['xml_file']}")
        json_response = dataset.upload(xml_file, session).json()
        # json_response = helpers.simulate_upload_json_response()
        geonetwork_uuid = helpers.get_geonetwork_uuid(json_response)

        row['geonetwork_uuid'] = geonetwork_uuid

        rows_to_dump.append(row)


    output_file = f"{__location__}/fixtures/generated/test.csv"

    new_file = f"{__location__}/fixtures/generated/test2.csv"

    helpers.dump_uploaded_uuid(rows_to_dump, output_file)
    helpers.replace_uuid(output_file, new_file)

    postponed_list = helpers.read_postponed_values(new_file)
    dataset.edit_postponed_values(postponed_list, session)

#region main entrypoint
if __name__ == "__main__":
    main()
#endregion
