import io
import uuid
from app.sql_dependant.sql_tables import User
from app.sql_dependant.sql_write import Update
from .settings import F_CLIENT_ID,F_CLIENT_SECRET
from . import app
from flask import request,redirect,escape,session,url_for,flash
from dateutil.relativedelta import relativedelta
import requests
import datetime
from uuid import uuid4
from . import utils
from app.sql_dependant.sql_connection import sqlconn
from app.sql_dependant.sql_read import Select
from werkzeug.datastructures import FileStorage
from app.helpers import project_dir,profile_photos_dir
fcallbackurl = "https://serdarbsgn.com/f-callback"


@app.route("/facebook-register",methods = ["GET"])
def facebook_sign_in():
    expire_at = str(datetime.datetime.now()+relativedelta(minutes=4))
    state = utils.generate_jwt_token({"expire_at":expire_at,"token":str(uuid4())})
    return redirect(f"""https://www.facebook.com/v16.0/dialog/oauth?client_id={F_CLIENT_ID}&redirect_uri={fcallbackurl}&state={state}&response_type=code&scope=public_profile+email""")


@app.route("/f-callback",methods = ["GET"])
def facebook_callback():
    code = request.args.get("code")
    state = request.args.get('state')
    state = utils.decode_jwt_token(state)
    if not state:
        return "Invalid state token",400
    if datetime.datetime.now() > datetime.datetime.strptime(state["expire_at"],"%Y-%m-%d %H:%M:%S.%f"):
        return "Token expired",400
    try:
        userinfo_response = requests.get(f"""https://graph.facebook.com/v16.0/oauth/access_token?client_id={F_CLIENT_ID}&redirect_uri={fcallbackurl}&client_secret={F_CLIENT_SECRET}&code={code}""")
        # use access token to get user data
        response = requests.get(
            'https://graph.facebook.com/me',
            params={
                'fields': 'id,email,first_name,last_name,picture',
                'access_token': userinfo_response.json()["access_token"]
            }
        )
        user_data = response.json()
    except:
        return "Something went wrong", 400
    # Do something with the user data (e.g. register or log in the user)
    if "email" in user_data:
        with sqlconn() as sql:
            exists = sql.session.execute(Select.user_oauth2_email_exists(user_data)).mappings().fetchone()
            if not exists:
                role = state["role"]
                if facebook_register_func(user_data,role):
                    pass
                else:
                    return "Something went wrong",400
            exists = sql.session.execute(Select.user_oauth2_email_exists(user_data)).mappings().fetchone()
            if exists:
                session["user"] = exists["id"]
                return redirect(url_for('home')),200
            flash("Something went wrong"),400
            return redirect(url_for('home')),200
    else:
        return "User email not available or not verified by Facebook.", 400
    
def facebook_register_func(facebook_info):
    user = User(
    username=escape(f"{uuid4()}"[0:24]),
    email= facebook_info["email"],
    password=None)
    
    with sqlconn() as sql:
        try:
            sql.session.add(user)
            sql.commit()
            if "picture" in facebook_info:
                picture_url = facebook_info["picture"]["data"]["url"]
                photo = requests.get(picture_url)
                if photo.status_code == 200:
                    file_like_obj = io.BytesIO(file.content)
                    rand= "pp-"+str(uuid.uuid4())+".jpg"
                    file = FileStorage(file_like_obj, filename=project_dir+"/static/"+profile_photos_dir+rand)
                    sql.session.execute(Update.user_profile_picture({"id":user.username,"profile_picture":rand}))
                    sql.commit()
            return True
        except:
            sql.session.rollback()
            return False
        