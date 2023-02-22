"""Load .env values
"""

from dotenv import dotenv_values, find_dotenv

config = {
    **dotenv_values(find_dotenv(".env.shared")),
    **dotenv_values(find_dotenv(".env.secret")),
}

api_route_me = config["GEONETWORK"] + config["API_PATH"] + "/me"
api_route_records = config["GEONETWORK"] + config["API_PATH"] + "/records"
api_route_batchediting = api_route_records + "/batchediting"
