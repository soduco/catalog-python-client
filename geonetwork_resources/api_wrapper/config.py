from dotenv import dotenv_values

config = {
    **dotenv_values(".env"),  # load shared environment variables
    # **os.environ,  # override loaded values with environment variables
}

api_endpoint = config["GEONETWORK"] + config["API_PATH"]