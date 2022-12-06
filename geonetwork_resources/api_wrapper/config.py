from dotenv import dotenv_values

config = {
    **dotenv_values(".env"),  # load shared environment variables
    # **os.environ,  # override loaded values with environment variables
}

api_route_me = config["GEONETWORK"] + config["API_PATH"] + "/me"
api_route_records = config["GEONETWORK"] + config["API_PATH"] + "/records"
api_route_batchediting = api_route_records + "/batchediting"