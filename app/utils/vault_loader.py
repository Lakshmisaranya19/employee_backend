import hvac
import os
from dotenv import load_dotenv

load_dotenv()  # Load VAULT_ROLE_ID and VAULT_SECRET_ID from .env

VAULT_URL = "http://127.0.0.1:8200"
ROLE_ID = os.getenv("VAULT_ROLE_ID")
SECRET_ID = os.getenv("VAULT_SECRET_ID")

def load_secrets_from_vault():
    client = hvac.Client(url=VAULT_URL)

    # Authenticate with AppRole
    login = client.auth.approle.login(role_id=ROLE_ID, secret_id=SECRET_ID)
    client.token = login['auth']['client_token']

    # Fetch secrets from KV v2
    secrets = client.secrets.kv.v2.read_secret_version(path="myapp")
    return secrets['data']['data']
