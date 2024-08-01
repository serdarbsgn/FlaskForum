from typing import Union
from main import app
from fastapi import HTTPException, Request

from sql_dependant.sql_read import Select
from sql_dependant.sql_tables import   User
from sql_dependant.sql_connection import sqlconn
from sql_dependant.sql_write import  Delete, Update
from pydantic import BaseModel
from utils import check_auth

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
    
