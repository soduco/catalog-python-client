from typing import List
import requests
from . import config
from uuid import UUID

 #region DELETE
 
def delete_records(uuid_list: List[UUID], backup_records: bool=True, session: requests.Session=requests.session()):
    """ delete one or more records from their uuid """
    # TODO : ensure that the session is "logged in" ?
    token = session.cookies.get_dict().get("XSRF-TOKEN")
    opts = {
        "headers": {
            "X-XSRF-TOKEN": token,
            "accept": "application/json"
        }
    }
    params = {
        "uuids": uuid_list,
        "withBackup": backup_records
    }
    
    response = session.delete(config.api_route_records, params=params, **opts)
    response.raise_for_status()
    return response
