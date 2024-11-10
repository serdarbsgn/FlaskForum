from html import escape
import io
import os
import uuid
from views_api import TokenResponse
from sql_dependant.sql_connection import sqlconn
from sql_dependant.sql_read import Select
from sql_dependant.sql_tables import User
from sql_dependant.sql_write import Update
from sql_dependant import env_init
import requests
from main import app
import datetime
from dateutil.relativedelta import relativedelta
import utils
from uuid import uuid4
from helpers import flask_dir,profile_photos_dir
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import Query

callbackurl = "https://serdarbisgin.com.tr/callback"#This'll redirect to frontend, which'll communicate with /api/callback

@app.get("/api/google-register")
def google_sign_in():
    expire_at = str(datetime.datetime.now()+relativedelta(minutes=4))
    state = utils.generate_jwt_token({"expire_at":expire_at,"token":str(uuid4())})
    r_url = f'https://accounts.google.com/o/oauth2/auth?client_id={env_init.CLIENT_ID}&redirect_uri={callbackurl}&state={state}&response_type=code&scope=profile+email'
    return RedirectResponse(url=r_url)

@app.get("/api/callback")
async def google_callback(
    state: str = Query(..., description="State parameter from Google OAuth callback"),
    code: str = Query(..., description="Authorization code from Google OAuth callback")
):
    state = utils.decode_jwt_token(state)
    if not state:
        return JSONResponse(content={"detail": "Invalid state token"}, status_code=400)
    if datetime.datetime.now() > datetime.datetime.strptime(state["expire_at"],"%Y-%m-%d %H:%M:%S.%f"):
        return JSONResponse(content={"detail": "Token expired"}, status_code=400)
    try:
        token_endpoint = "https://oauth2.googleapis.com/token"
        token_response = requests.post(token_endpoint, data={
            "code": code,
            "client_id": env_init.CLIENT_ID,
            "client_secret": env_init.CLIENT_SECRET,
            "redirect_uri": callbackurl,
            "grant_type": "authorization_code"
        })
        token_data = token_response.json()
        access_token = token_data["access_token"]
        
        userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"
        userinfo_response = requests.get(userinfo_endpoint, headers={
            "Authorization": f"Bearer {access_token}"
        })
        g_user_data = userinfo_response.json()
    except:
        JSONResponse(content={"detail": "Something went wrong."}, status_code=400)
    if userinfo_response.json().get("email_verified"):
        with sqlconn() as sql:
            exists = sql.session.execute(Select.user_oauth2_email_exists(g_user_data)).mappings().fetchone()
            if not exists:
                if google_register_func(g_user_data):
                    pass
                else:
                    sql.close()
                    JSONResponse(content={"detail": "Something went wrong."}, status_code=400)
                #Do register stuff
            exists = sql.session.execute(Select.user_oauth2_email_exists(g_user_data)).mappings().fetchone()
            if exists:
                expire_at = str(datetime.datetime.now()+relativedelta(hours=4))
                auth_jwt_token = utils.generate_jwt_token({"expire_at":expire_at,"user":exists["id"]})
                return TokenResponse(token = auth_jwt_token)
            return JSONResponse(content={"detail": "Something went wrong."}, status_code=400)
    else:
        return "User email not available or not verified by Google.", 400
    
async def google_register_func(google_info):
    user = User(
    username=escape(f"{uuid4()}"[0:24]),
    email= google_info["email"],
    password=None)  
    with sqlconn() as sql:
        try:
            sql.session.add(user)
            sql.commit()
            if "picture" in google_info:
                photo = requests.get(google_info["picture"])
                if photo.status_code == 200:
                    file_like_obj = io.BytesIO(photo.content)
                    rand= "pp-"+str(uuid.uuid4())+".jpg"
                    filepath = os.path.join(flask_dir,"static",profile_photos_dir,rand)
                    with open(filepath, "wb") as buffer:
                        buffer.write(await file_like_obj.read())
                    sql.session.execute(Update.user_profile_picture({"id":str(user.username),"profile_picture":rand}))
                    sql.commit()
            return True
        except:
            sql.session.rollback()
            return False
