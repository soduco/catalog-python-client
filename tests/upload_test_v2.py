"""script to test parse, upload and update_pstponed_values functions in one script"""

import os
import csv

from soduco_geonetwork.api_wrapper import (config, dataset, geonetwork,
                                              yaml_to_xml, helpers)


def main():
    """
        Read fixtures/instance.yaml
        Build XML records
        Upload them on catalog
    """

    session = geonetwork.log_in(config.config['GEONETWORK_USER'],
                                config.config['GEONETWORK_PASSWORD'])

    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
    output_dir = f"{__location__}/fixtures/generated"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    yaml_to_xml.parse(input_file=f"{__location__}/fixtures/instance.yaml",
                            output_folder=f"{output_dir}")

    rows_to_dump = []

    filepath = os.path.join(f"{__location__}/yaml_list.csv")

    file = open(filepath, 'r', encoding='utf8')
    reader = csv.DictReader(file)
    for row in reader:
        xml_file = helpers.read_xml_file(f"{row['xml_file_path']}")
        json_response = dataset.upload(xml_file, session).json()
        # json_response = helpers.simulate_upload_json_response()
        geonetwork_uuid = helpers.get_geonetwork_uuid(json_response)

        row['geonetwork_uuid'] = geonetwork_uuid

        rows_to_dump.append(row)

    output_file = f"{output_dir}/test.csv"
    helpers.dump_uploaded_uuid(rows_to_dump, output_file)

    new_file = f"{output_dir}/test2.csv"
    helpers.replace_uuid(output_file, new_file)
    postponed_list = helpers.read_postponed_values(new_file)

    for item in postponed_list:
        dataset.edit_postponed_values(item, session)

#region main entrypoint
if __name__ == "__main__":
    main()
#endregion
