import io
import uuid
from app.sql_dependant.sql_connection import sqlconn
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import User
from app.sql_dependant.sql_write import Update
from .settings import CLIENT_ID,CLIENT_SECRET
import requests
from . import app
from flask import request,redirect,escape,session,flash,url_for
import datetime
from dateutil.relativedelta import relativedelta
from . import utils
from uuid import uuid4
from werkzeug.datastructures import FileStorage
from app.helpers import project_dir,profile_photos_dir
callbackurl = "https://serdarbsgn.com/callback"

@app.route("/google-register",methods = ["GET"])
def google_sign_in():
    expire_at = str(datetime.datetime.now()+relativedelta(minutes=4))
    state = utils.generate_jwt_token({"expire_at":expire_at,"token":str(uuid4())})
    return redirect(f'https://accounts.google.com/o/oauth2/auth?client_id={CLIENT_ID}&redirect_uri={callbackurl}&state={state}&response_type=code&scope=profile+email')

@app.route("/callback",methods = ["GET"])
def google_callback():
    code = request.args.get("code")
    state = request.args.get('state')
    state = utils.decode_jwt_token(state)
    if not state:
        return "Invalid state token",400
    if datetime.datetime.now() > datetime.datetime.strptime(state["expire_at"],"%Y-%m-%d %H:%M:%S.%f"):
        return "Token expired",400
    try:
        token_endpoint = "https://oauth2.googleapis.com/token"
        token_response = requests.post(token_endpoint, data={
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
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
        return "Something went wrong", 400
    if userinfo_response.json().get("email_verified"):
        with sqlconn() as sql:
            exists = sql.session.execute(Select.user_oauth2_email_exists(g_user_data)).mappings().fetchone()
            if not exists:
                if google_register_func(g_user_data):
                    pass
                else:
                    sql.close()
                    return "Something went wrong", 400
                #Do register stuff
            exists = sql.session.execute(Select.user_oauth2_email_exists(g_user_data)).mappings().fetchone()
            if exists:
                session["user"] = exists["id"]
                return redirect(url_for('home')),200
            flash("Something went wrong"),400
            return redirect(url_for('home')),200
    else:
        return "User email not available or not verified by Google.", 400
    
def google_register_func(google_info):
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
                    file = FileStorage(file_like_obj, filename=rand)
                    file.save(project_dir+"/static"+profile_photos_dir+rand)
                    sql.session.execute(Update.user_profile_picture({"id":str(user.username),"profile_picture":rand}))
                    sql.commit()
            return True
        
        except:
            sql.session.rollback()
            return False
