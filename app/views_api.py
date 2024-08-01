from datetime import datetime
from typing import Any, Dict, Union
import uuid
from main import app
from fastapi import Depends, HTTPException, Request
from dateutil.relativedelta import relativedelta

from sql_dependant.sql_read import Select
from sql_dependant.sql_tables import   User
from sql_dependant.sql_connection import sqlconn
from sql_dependant.sql_write import  Delete, Update
from pydantic import BaseModel
from utils import check_auth, decode_jwt_token, generate_jwt_token,generate_hash

class UserInfo(BaseModel):
    username: str
    picture: str

class ErrorResponse(BaseModel):
    detail: str

@app.get('/api/userinfo',
        summary="Retrieve user information",
        description="This endpoint retrieves user information. An Authorization token must be included in the header.",
        responses={
        200: {
            "description": "User information retrieved successfully",
            "model": UserInfo
        },
        401: {
            "description": "Unauthorized, token is expired or invalid",
            "model": ErrorResponse
        }
        })
async def api_get_user_info(request: Request):
    auth_check = check_auth(request)
    if not auth_check:
        raise HTTPException(status_code=401, detail="Can't get the user because token is expired or wrong.")
    
    with sqlconn() as sql:
        user = sql.session.execute(Select.user_username({"id":auth_check["user"]})).mappings().fetchone()
        picture = sql.session.execute(Select.user_profile_picture({"user":user["username"]})).mappings().fetchone()
        if picture["profile_picture"] is None:
            picture = {"profile_picture": "pp.jpg"}
        return UserInfo(username=user["username"], picture=picture["profile_picture"])

class TokenResponse(BaseModel):
    token: str

@app.get('/api/login',
        summary="Get login token",
        description="This endpoint retrieves user login token to use while logging in.",
        responses={
        200: {
            "description": "Login token retrieved successfully",
            "model": TokenResponse
        }
        })
async def api_login_get():
    expire_at = str(datetime.now()+relativedelta(minutes=4))
    login_jwt_token = generate_jwt_token({"expire_at":expire_at,"token":str(uuid.uuid4()),"use":"login"})
    return TokenResponse(token = login_jwt_token)

class LoginInfo(BaseModel):
    token:str
    username: str
    password: str

async def validate_login_token(login_info: LoginInfo) -> Dict[str, Any]:
    token = login_info.token
    if not token:
        raise HTTPException(status_code=400, detail="Missing token")
    
    token_validity = decode_jwt_token(token)
    if not token_validity:
        raise HTTPException(status_code=400, detail="Not a valid token")
    if not set(["expire_at", "token", "use"]).issubset(set(token_validity.keys())):
        raise HTTPException(status_code=400, detail="Not a valid token")
    if token_validity["use"] != "login":
        raise HTTPException(status_code=400, detail="Not a valid token")
    if datetime.now() > datetime.strptime(token_validity["expire_at"], "%Y-%m-%d %H:%M:%S.%f"):
        raise HTTPException(status_code=400, detail="Token expired")
    
    return {"username":login_info.username,"password":login_info.password}

@app.post('/api/login',
        summary="Manage api login",
        description="This endpoint is for logging in.",
        responses={
        200: {
            "description": "Login was successful",
            "model": TokenResponse
        },
        400: {
            "description": "Something is wrong about the login token or json sent.",
            "model": ErrorResponse
        },
        401: {
            "description": "Supplied credentials are wrong.",
            "model": ErrorResponse
        },
        })
async def api_login_post(login_info: LoginInfo, token_validity: Dict[str, Any] = Depends(validate_login_token)):
        if not set(["username", "password"]).issubset(set(token_validity.keys())):
            raise HTTPException(status_code=400, detail="Crucial information about login is missing.")
        login_info = (token_validity["username"],token_validity["password"])
        with sqlconn() as sql:
            check = sql.session.execute(Select.user_exists_username_password(({"username":login_info[0],"password":generate_hash(login_info[1])}))).mappings().fetchall()
            if len(check)>0:
                expire_at = str(datetime.now()+relativedelta(hours=4))
                auth_jwt_token = generate_jwt_token({"expire_at":expire_at,"user":check[0]["id"]})
                return TokenResponse(token = auth_jwt_token)
            else: 
                raise HTTPException(status_code=400, detail="User with your supplied credentials does not exist")