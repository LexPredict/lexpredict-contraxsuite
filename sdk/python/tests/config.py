import openapi_client

HOST_NAME = 'http://127.0.0.1:3355'
ADMIN_USER_NAME = 'Administrator'
ADMIN_USER_PASSWORD = 'Administrator'

# these ^^ should be customized locally via local_config.py
try:
    from local_config import *
except:
    pass


base_configuration = openapi_client.Configuration(
    host=HOST_NAME,
    discard_unknown_keys=True,
)
