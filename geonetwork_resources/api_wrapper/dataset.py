import requests
from . import config


 #region DELETE
 
def delete_records(uuid_list: list, backup_records: bool, session: requests.Session=requests.session()):
    """ delete one or more records from their uuid """

    session = session or requests.session()
    
    # TODO : ensure that the session is "logged in" ?

    token = session.cookies.get_dict().get("XSRF-TOKEN")
    
    headers = {
        "X-XSRF-TOKEN": token,
        "accept": "application/json"
    }

    opts = {
        "headers": headers
    }
    
    params = {
        "uuids": uuid_list,
        "withBackup": backup_records
    }
    
    response = session.delete(config.api_route_records, params=params, **opts)
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

    delete_records(session=client, uuid_list=uuid_list, backup_records="true", cookies=cookies)
