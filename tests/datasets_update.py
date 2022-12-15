"""
    test batch edit from api
"""

import os
from geonetwork_resources.api_wrapper import geonetwork, config, helpers, dataset

__location__ = os.path.realpath(
os.path.join(os.getcwd(), os.path.dirname(__file__)))

def main():
    """
        main function
    """

    session = geonetwork.log_in(config.config["GEONETWORK_USER"],
                                config.config["GEONETWORK_PASSWORD"])

    uuid_list = helpers.uuid_list_from_csv(f'{__location__}/fixtures/test_uuids.csv')

    xpath_title = "mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:title>"

    if not uuid_list:
        print("The file fixtures/test_uuids.csv does not exist!")
    else:
        response = dataset.update(uuid_list, xpath_title, "This title was edited", session=session)
        print(response)


#region main entrypoint
if __name__ == "__main__":
    main()
#endregion
