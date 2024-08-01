from datetime import datetime
import jwt
from sql_dependant.env_init import JWT_SECRET_KEY,PASSWORD_SALT
from hashlib import pbkdf2_hmac

def decode_jwt_token(encoded_content):
    try:
        decoded_content = jwt.decode(encoded_content, JWT_SECRET_KEY, ["HS256"])
    except:
        decoded_content = False
    return decoded_content

def generate_jwt_token(content):
    encoded_content = jwt.encode(content, JWT_SECRET_KEY, algorithm="HS256")
    token = str(encoded_content)
    return token

def generate_hash(plain_password, password_salt=PASSWORD_SALT):
    password_hash = pbkdf2_hmac(
        "sha256",
        b"%b" % bytes(plain_password, "utf-8"),
        b"%b" % bytes(password_salt, "utf-8"),
        10000,
    )
    return password_hash.hex()

def check_auth(request):
    if not "Authorization" in request.headers:
        return False
    test = decode_jwt_token(request.headers['Authorization'])
    if test:
        if not set(["expire_at", "user"]).issubset(set(test.keys())):
            return False
        if datetime.now() < datetime.strptime(test["expire_at"],"%Y-%m-%d %H:%M:%S.%f"):
            return test
    return False

