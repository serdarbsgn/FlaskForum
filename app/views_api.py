import datetime
import logging
import uuid
from dateutil.relativedelta import relativedelta

from flask import  jsonify, request,escape
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import   User
from app.sql_dependant.sql_connection import sqlconn
from app.sql_dependant.sql_write import  Delete, Update
from app.utils import generate_hash,generate_jwt_token,decode_jwt_token
from PIL import Image
from . import app
from app.helpers import *

@app.route('/api/register', methods=['GET', 'POST'])
def api_register():
    if request.method == 'GET':
        expire_at = str(datetime.datetime.now()+relativedelta(minutes=4))
        register_jwt_token = generate_jwt_token({"expire_at":expire_at,"token":str(uuid.uuid4()),"use":"register"})
        return jsonify({"token":register_jwt_token}),200

    if request.method == 'POST':
        if 'token' not in request.json:
            return jsonify({"msg":"Missing token"}),400
        token_validity = decode_jwt_token(request.json["token"])
        if not token_validity:
            return jsonify({"msg":"Not a valid token"}),400
        if not set(["expire_at", "token", "use"]).issubset(set(token_validity.keys())):
            return jsonify({"msg":"Not a valid token"}),400
        if token_validity["use"] != "register":
            return jsonify({"msg":"Not a valid token"}),400
        if datetime.datetime.now() > datetime.datetime.strptime(token_validity["expire_at"],"%Y-%m-%d %H:%M:%S.%f"):
            return jsonify({"msg":"Token expired"}),400
        if not set(["username", "email", "password"]).issubset(set(request.json.keys())):
            return jsonify({"msg":"Crucial information about register is missing."}),400
        register_info = (request.json["username"],request.json["email"],request.json["password"])
        for el in register_info:
            if not isinstance(el,str) or len(el) == 0:
                return jsonify({"msg":"All register info must be a string and not empty"}),400
        if len(register_info[0]) < 4 or 20 < len(register_info[0]):
            return jsonify({"msg":"Username too long or short"}),400
        if register_info[1].find("@") == -1:
            return jsonify({"msg":"This doesn't look like an email"}),400
        if len(register_info[2]) < 8 or 80 < len(register_info[2]):
            return jsonify({"msg":"Password too long or short"}),400
        user = User(
            username=escape(register_info[0]),
            email=escape(register_info[1]),
            password=generate_hash(escape(register_info[2])))
        with sqlconn() as sql:
            check = sql.session.execute(Select.user_unique_username_email({"username":user.username,"email":user.email})).mappings().fetchall()
            if len(check)>0:
                return jsonify({"msg":"Email and/or Username already exists"}),400
            sql.session.add(user)
            sql.session.commit()
            return jsonify({"msg":"User created successfully"}),200

@app.route('/api/login', methods=['GET', 'POST'])
def api_login():
    if request.method == 'GET':
        expire_at = str(datetime.datetime.now()+relativedelta(minutes=4))
        login_jwt_token = generate_jwt_token({"expire_at":expire_at,"token":str(uuid.uuid4()),"use":"login"})
        return jsonify({"token":login_jwt_token}),200
    
    if request.method == 'POST':
        if 'token' not in request.json:
            return jsonify({"msg":"Missing token"}),400
        token_validity = decode_jwt_token(request.json["token"])
        if not token_validity:
            return jsonify({"msg":"Not a valid token"}),400
        if not set(["expire_at", "token", "use"]).issubset(set(token_validity.keys())):
            return jsonify({"msg":"Not a valid token"}),400
        if token_validity["use"] != "login":
            return jsonify({"msg":"Not a valid token"}),400
        if datetime.datetime.now() > datetime.datetime.strptime(token_validity["expire_at"],"%Y-%m-%d %H:%M:%S.%f"):
            return jsonify({"msg":"Token expired"}),400
        if not set(["username", "password"]).issubset(set(request.json.keys())):
            return jsonify({"msg":"Crucial information about login is missing."}),400
        login_info = (request.json["username"],request.json["password"])
        sql = sqlconn()
        check = sql.session.execute(Select.user_exists_username_password(({"username":login_info[0],"password":generate_hash(login_info[1])}))).mappings().fetchall()
        if len(check)>0:
            expire_at = str(datetime.datetime.now()+relativedelta(hours=4))
            auth_jwt_token = generate_jwt_token({"expire_at":expire_at,"user":check[0]["id"]})
            return jsonify({"msg":"Login was successful","token":auth_jwt_token}),200
        else: 
            return jsonify({"msg":"User with your supplied credentials does not exist"}),401

@app.route('/api/userinfo', methods=['GET'])
def api_get_user_info():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    with sqlconn() as sql:
        user = sql.session.execute(Select.user_username({"id":auth_check["user"]})).mappings().fetchone()
        picture = sql.session.execute(Select.user_profile_picture({"user":user["username"]})).mappings().fetchone()
        if picture["profile_picture"] is None:
            picture = {"profile_picture": "pp.jpg"}
        return jsonify({"username":user["username"],"picture":picture["profile_picture"]}),200

def check_auth():
    if not "Authorization" in request.headers:
        return False
    test = decode_jwt_token(request.headers['Authorization'])
    if test:
        if not set(["expire_at", "user"]).issubset(set(test.keys())):
            return False
        if datetime.datetime.now() < datetime.datetime.strptime(test["expire_at"],"%Y-%m-%d %H:%M:%S.%f"):
            return test
    return False

@app.route('/api/change-username', methods=['POST'])
def api_change_username():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    if not set(["username"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    if len(escape(request.json["username"])) < 4 or 20 < len(escape(request.json["username"])):
            return jsonify({"msg":"Username too long or short"}),400
    with sqlconn() as sql:
        check = sql.session.execute(Select.user_unique_username({"username":escape(request.json["username"])})).mappings().fetchall()
        if len(check)>0:
            return jsonify({"msg":"Requested username already exists"}),400
        
        sql.session.execute(Update.user_username({"id":auth_check["user"],"username":escape(request.json["username"])}))
        sql.session.commit()
        return jsonify({"msg":"Username changed successfully"}),200

@app.route('/api/change-password', methods=['POST'])
def api_change_password():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    if not set(["current_password","new_password"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    if len(request.json["new_password"]) < 8 or 80 < len(request.json["new_password"]):
        return jsonify({"msg":"New password is too long or short"}),400
    with sqlconn() as sql:
        check = sql.session.execute(Select.user_exists_id_password({"user_id":auth_check["user"],
        "password":generate_hash(escape(request.json["current_password"]))})).mappings().fetchall()
        if len(check)==0:
            return jsonify({"msg":"Entered current password is incorrect"}),400
        sql.session.execute(Update.user_password({"user_id":auth_check["user"],"password":generate_hash(escape(request.json["new_password"]))}))
        sql.session.commit()
        return jsonify({"msg":"Password changed successfully"}),200
    
@app.route('/api/set-password', methods=['POST'])
def api_set_password():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    if not set(["new_password"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    if len(request.json["new_password"]) < 8 or 80 < len(request.json["new_password"]):
        return jsonify({"msg":"New password is too long or short"}),400
    with sqlconn() as sql:
        check = sql.session.execute(Select.user_exists_id_none_password({"user_id":auth_check["user"]})).mappings().fetchall()
        if len(check)==0:
            return jsonify({"msg":"This is only for the users registered with OAUTH2 methods."}),400
        sql.session.execute(Update.user_password({"user_id":auth_check["user"],"password":generate_hash(escape(request.json["new_password"]))}))
        sql.session.commit()
        return jsonify({"msg":"Password set successfully"}),200

@app.route('/api/remove-account', methods=['POST'])
def api_remove_account():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    if not set(["username"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    if len(escape(request.json["username"])) < 4 or 20 < len(escape(request.json["username"])):
        return jsonify({"msg":"Write your username correctly to delete your account."}),400
    with sqlconn() as sql:
        get_user = sql.session.execute(Select.user_username({"id":auth_check["user"]})).mappings().fetchone()
        username = get_user["username"]
        if str(escape(request.json["username"])) == username:
            get_user_pp_location = sql.session.execute(Select.user_profile_picture({"user":username})).mappings().fetchone()
            if get_user_pp_location["profile_picture"]:
                try:
                    os.remove(project_dir+"/static/"+profile_photos_dir+get_user_pp_location["profile_picture"])
                except FileNotFoundError:
                    pass
            sql.session.execute(Delete.user({"id":auth_check["user"],"username":username}))
            sql.commit()
            return jsonify({"msg":"Removed profile picture and all the info about you successfully."}),200
        return jsonify({"msg":"Write your username correctly to delete your account."}),400
                
            
#There is no real logout since authentication is done by jwt unless we use some in-memory blacklist(like redis) to check.

@app.route('/api/userstats', methods=['GET'])
def api_userstats():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    with sqlconn() as sql:
        user_scores = {
            "comment_count":sql.session.execute(Select.user_comment_count({"user_id":auth_check["user"]})).mappings().fetchone()["count"],
            "post_count":sql.session.execute(Select.user_post_count({"user_id":auth_check["user"]})).mappings().fetchone()["count"],
            "comment_karma":sql.session.execute(Select.user_karma_point_comment({"user_id":auth_check["user"]})).mappings().fetchone()["sum"],
            "post_karma":sql.session.execute(Select.user_karma_point_post({"user_id":auth_check["user"]})).mappings().fetchone()["sum"]
        }
        return jsonify({"scores":user_scores}),200

# Not finished yet.
@app.route('/api/add-profile-picture', methods=['POST'])
def api_add_profile_picture():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    if 'file' not in request.files:
        return jsonify({"msg":"No file"}),400
    with sqlconn() as sql:
        user_info = sql.session.execute(Select.user_username({"id":auth_check["user"]})).mappings().fetchone()
        rand= "pp-"+str(uuid.uuid4())+".jpg"
        filepath = project_dir+"/static"+profile_photos_dir+rand
        file = request.files['file']
        file.save(filepath)
        try:
            img = Image.open(filepath)
            img.verify()
            img.close()
        except:
            os.remove(filepath)
            return jsonify({"msg":"This is not an image"}),400
        sql.session.execute(Update.user_profile_picture({"id":user_info["username"],"profile_picture":rand}))
        sql.commit()
        return jsonify({"msg":"Picture added successfully!"}),200

@app.route('/api/remove-profile-picture', methods=['GET'])
def api_remove_profile_picture():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
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
        return jsonify({"msg":"Removed profile picture successfully."}),200


from app import comments_views_api,forums_views_api,posts_views_api,views_market_api