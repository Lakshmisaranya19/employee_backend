from app.utils.vault_loader import load_secrets_from_vault

secrets = load_secrets_from_vault()

DATABASE_URL = secrets["DATABASE_URL"]
SECRET_KEY = secrets["SECRET_KEY"]
ALGORITHM = secrets.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(secrets.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
SENDGRID_API_KEY = secrets["SENDGRID_API_KEY"]
FROM_EMAIL = secrets["FROM_EMAIL"]

