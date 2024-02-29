#For sql required stuff.
from dotenv import load_dotenv
import os
load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")
SECRET_KEY = os.urandom(32)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
PASSWORD_SALT = os.getenv("PASSWORD_SALT")