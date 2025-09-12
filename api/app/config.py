import os

API_PREFIX = "/api/v1"
DB_NAME = os.environ.get("DB_NAME", "api")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "api")
DB_PASS = os.environ.get("DB_PASS", "1234qwe")
PRODUCTION_DATABASE_PATH = f"{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
APP_PORT = 5000
APP_HOST = "0.0.0.0"
APP_VERSION = "v2"
SQLALCHEMY_URI_KEY_NAME = os.environ.get(
    "SQLALCHEMY_URI_KEY_NAME", "rtyuioiuytgrfdsddfghjk"
)
