from datetime import datetime
from html import escape
import logging
import os
from typing import Any, Dict
import uuid
from main import app
from fastapi import Depends, File, HTTPException, Request, UploadFile
from dateutil.relativedelta import relativedelta
from PIL import Image
from sql_dependant.sql_read import Select
from sql_dependant.sql_tables import   User
from sql_dependant.sql_connection import sqlconn
from sql_dependant.sql_write import  Delete, Update
from pydantic import BaseModel, EmailStr, Field
from utils import check_auth, decode_jwt_token, generate_jwt_token,generate_hash
from helpers import project_dir,profile_photos_dir

class UserInfo(BaseModel):
    username: str
    picture: str

class ErrorResponse(BaseModel):
    detail: str
class MsgResponse(BaseModel):
    msg : str
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
    username: str = Field(min_length=4, max_length=20)
    password: str = Field(min_length=8, max_length=20)

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
        }
        })
async def api_login_post(login_info: LoginInfo, token_validity: Dict[str, Any] = Depends(validate_login_token)):
        login_info = (token_validity["username"],token_validity["password"])
        with sqlconn() as sql:
            check = sql.session.execute(Select.user_exists_username_password(({"username":login_info[0],"password":generate_hash(login_info[1])}))).mappings().fetchall()
            if len(check)>0:
                expire_at = str(datetime.now()+relativedelta(hours=4))
                auth_jwt_token = generate_jwt_token({"expire_at":expire_at,"user":check[0]["id"]})
                return TokenResponse(token = auth_jwt_token)
            else: 
                raise HTTPException(status_code=400, detail="User with your supplied credentials does not exist")
            
@app.get('/api/register',
        summary="Get register token",
        description="This endpoint retrieves user register token to use while registering.",
        responses={
        200: {
            "description": "Register token retrieved successfully",
            "model": TokenResponse
        }
        })
async def api_register_get():
        expire_at = str(datetime.now()+relativedelta(minutes=4))
        register_jwt_token = generate_jwt_token({"expire_at":expire_at,"token":str(uuid.uuid4()),"use":"register"})
        return TokenResponse(token = register_jwt_token)


class RegisterInfo(BaseModel):
    token:str
    username: str = Field(min_length=4, max_length=20)
    email:EmailStr
    password: str = Field(min_length=8, max_length=20)

async def validate_register_token(register_info: RegisterInfo) -> Dict[str, Any]:
    token = register_info.token
    if not token:
        raise HTTPException(status_code=400, detail="Missing token")
    token_validity = decode_jwt_token(token)
    if not token_validity:
        raise HTTPException(status_code=400, detail="Not a valid token")
    if not set(["expire_at", "token", "use"]).issubset(set(token_validity.keys())):
        raise HTTPException(status_code=400, detail="Not a valid token")
    if token_validity["use"] != "register":
        raise HTTPException(status_code=400, detail="Not a valid token")
    if datetime.now() > datetime.strptime(token_validity["expire_at"],"%Y-%m-%d %H:%M:%S.%f"):
        raise HTTPException(status_code=400, detail="Token expired")
    return {"username":register_info.username,"email":register_info.email,"password":register_info.password}

@app.post('/api/register',
        summary="Manage api register",
        description="This endpoint is for registering.",
        responses={
        200: {
            "description": "Registration was successful",
            "model": MsgResponse
        },
        401: {
            "description": "Something is wrong about the authorization token or json sent.",
            "model": ErrorResponse
        },
        400: {
            "description": "Email and/or Username already exists.",
            "model": ErrorResponse
        },
        })
async def api_register_post(register_info: RegisterInfo, token_validity: Dict[str, Any] = Depends(validate_register_token)):
        register_info = (token_validity["username"],token_validity["email"],token_validity["password"])
        user = User(
            username=escape(register_info[0]),
            email=escape(register_info[1]),
            password=generate_hash(escape(register_info[2])))
        with sqlconn() as sql:
            check = sql.session.execute(Select.user_unique_username_email({"username":user.username,"email":user.email})).mappings().fetchall()
            if len(check)>0:
                raise HTTPException(status_code=400, detail="Email and/or Username already exists")
            sql.session.add(user)
            sql.session.commit()
            return MsgResponse(msg="User created successfully")
        


class UsernameInfo(BaseModel):
    username: str = Field(min_length=4, max_length=20)

@app.post('/api/change-username',
        summary="Change username",
        description="This endpoint is for changing username.",
        responses={
        200: {
            "description": "Username changed.",
            "model": MsgResponse
        },
        401: {
            "description": "Something is wrong about the authorization token or json sent.",
            "model": ErrorResponse
        },
        400: {
            "description": "Username already exists.",
            "model": ErrorResponse
        },
        })
async def api_change_username(request:Request,username_info:UsernameInfo):
    auth_check = check_auth(request)
    with sqlconn() as sql:
        check = sql.session.execute(Select.user_unique_username({"username":escape(request.json["username"])})).mappings().fetchall()
        if len(check)>0:
            raise HTTPException(status_code=400, detail="Requested username already exists")
        
        sql.session.execute(Update.user_username({"id":auth_check["user"],"username":escape(username_info.username)}))
        sql.session.commit()
        return MsgResponse(msg="Username changed successfully")

class PasswordChangeInfo(BaseModel):
    current_password: str = Field(min_length=8, max_length=20)
    new_password: str = Field(min_length=8, max_length=20)

@app.post('/api/change-password')
async def api_change_password(request:Request,password_info:PasswordChangeInfo):
    auth_check = check_auth(request)
    with sqlconn() as sql:
        check = sql.session.execute(Select.user_exists_id_password({"user_id":auth_check["user"],
        "password":generate_hash(escape(password_info.current_password))})).mappings().fetchall()
        if len(check)==0:
            raise HTTPException(status_code=400, detail= "Entered current password is incorrect")
        sql.session.execute(Update.user_password({"user_id":auth_check["user"],"password":generate_hash(escape(password_info.new_password))}))
        sql.session.commit()
        return MsgResponse(msg="Password changed successfully")
    
class PasswordSetInfo(BaseModel):
    new_password: str = Field(min_length=8, max_length=20)   

@app.post('/api/set-password')
async def api_set_password(request:Request,password_info:PasswordSetInfo):
    auth_check = check_auth(request)
    with sqlconn() as sql:
        check = sql.session.execute(Select.user_exists_id_none_password({"user_id":auth_check["user"]})).mappings().fetchall()
        if len(check)==0:
            raise HTTPException(status_code=400, detail="This is only for the users registered with OAUTH2 methods.")
        sql.session.execute(Update.user_password({"user_id":auth_check["user"],"password":generate_hash(escape(password_info.new_password))}))
        sql.session.commit()
        return MsgResponse(msg="Password set successfully")

@app.post('/api/remove-account',
        responses={
        200: {
            "description": "Success response",
            "model": MsgResponse
        },
        401: {
            "description": "Something is wrong about the authorization token or json sent.",
            "model": ErrorResponse
        },
        400: {
            "description": "Entered username is incorrect",
            "model": ErrorResponse
        }
        })
async def api_remove_account(request:Request,username_info:UsernameInfo):
    auth_check = check_auth(request)
    with sqlconn() as sql:
        get_user = sql.session.execute(Select.user_username({"id":auth_check["user"]})).mappings().fetchone()
        username = get_user["username"]
        if escape(username_info.username) == username:
            get_user_pp_location = sql.session.execute(Select.user_profile_picture({"user":username})).mappings().fetchone()
            if get_user_pp_location["profile_picture"]:
                try:
                    os.remove(project_dir+"/static/"+profile_photos_dir+get_user_pp_location["profile_picture"])
                except FileNotFoundError:
                    pass
            sql.session.execute(Delete.user({"id":auth_check["user"],"username":username}))
            sql.commit()
            return MsgResponse(msg="Removed profile picture and all the info about you successfully.")
        raise HTTPException(status_code=400, detail="Write your username correctly to delete your account.")
    
class UserScores(BaseModel):
    comment_count: int
    post_count: int
    comment_karma: int
    post_karma: int

class UserStatsResponse(BaseModel):
    scores: UserScores

@app.get('/api/userstats',
        responses={
        200: {
            "description": "User Stats.",
            "model": UserStatsResponse
        },
        401: {
            "description": "Something is wrong about the authorization token or json sent.",
            "model": ErrorResponse
        }})
async def api_userstats(request:Request):
    auth_check = check_auth(request)
    with sqlconn() as sql:
        user_scores = {
            "comment_count":sql.session.execute(Select.user_comment_count({"user_id":auth_check["user"]})).mappings().fetchone()["count"],
            "post_count":sql.session.execute(Select.user_post_count({"user_id":auth_check["user"]})).mappings().fetchone()["count"],
            "comment_karma":sql.session.execute(Select.user_karma_point_comment({"user_id":auth_check["user"]})).mappings().fetchone()["sum"],
            "post_karma":sql.session.execute(Select.user_karma_point_post({"user_id":auth_check["user"]})).mappings().fetchone()["sum"]
        }
        return UserStatsResponse(scores=UserScores(comment_count=user_scores["comment_count"],post_count=user_scores["post_count"],comment_karma=user_scores["comment_karma"],post_karma=user_scores["post_karma"]))

@app.post('/api/add-profile-picture',
        responses={
        200: {
            "description": "Success response",
            "model": MsgResponse
        },
        401: {
            "description": "Something is wrong about the authorization token or json sent.",
            "model": ErrorResponse
        },
        400: {
            "description": "Sent file is not an image.",
            "model": ErrorResponse
        }
        })
async def api_add_profile_picture(request:Request,file: UploadFile = File(...)):
    auth_check = check_auth(request)
    rand = "pp-" + str(uuid.uuid4()) + ".jpg"
    filepath = os.path.join(project_dir, "static", profile_photos_dir, rand)
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())
    try:
        img = Image.open(filepath)
        img.verify()
    except (IOError, SyntaxError):
        os.remove(filepath)
        raise HTTPException(status_code=400, detail="This is not a valid image")

    with sqlconn() as sql:
        user_info = sql.session.execute(Select.user_username({"id":auth_check["user"]})).mappings().fetchone()
        sql.session.execute(Update.user_profile_picture({"id":user_info["username"], "profile_picture":rand}))
        sql.commit()
    
    return MsgResponse(msg="Picture added successfully!")

@app.get('/api/remove-profile-picture',
        responses={
        200: {
            "description": "Success response",
            "model": MsgResponse
        },
        401: {
            "description": "Something is wrong about the authorization token or json sent.",
            "model": ErrorResponse
        }
        })
async def api_remove_profile_picture(request:Request):
    auth_check = check_auth(request)
    with sqlconn() as sql:
        user = sql.session.execute(Select.user_username({"id":auth_check["user"]})).mappings().fetchone()
        picture = sql.session.execute(Select.user_profile_picture({"user":user["username"]})).mappings().fetchone()
        sql.session.execute(Update.user_profile_picture({"id":user["username"],"profile_picture":None}))
        sql.commit()
        try:
            os.remove(project_dir+"/static"+profile_photos_dir+picture["profile_picture"])
        except FileNotFoundError:
            pass
        except Exception as e:
            logging.warn(e)
        return MsgResponse(msg="Removed profile picture successfully.")
    
import comments_views_api,forums_views_api,posts_views_api