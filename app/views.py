import uuid

from app.flaskforms import  ChangePasswordForm, RegisterForm,LoginForm,AddProfilePicture, SetPasswordForm, UsernameForm
from flask import  redirect, url_for,render_template,session,flash,request,escape
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import   User
from app.sql_dependant.sql_connection import sqlconn
from app.sql_dependant.sql_write import  Delete, Update
from app.utils import generate_hash
from PIL import Image
from . import app
from app.helpers import *

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=escape(form.username._value()),
            email=escape(form.email._value()),
            password=generate_hash(escape(form.password._value())))
        with sqlconn() as sql:
            check = sql.session.execute(Select.user_unique_username_email({"username":user.username,"email":user.email})).mappings().fetchall()
            if len(check)>0:
                flash("Email and/or Username already exists")
                return "Email and/or Username already exists",400
            sql.session.add(user)
            sql.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        sql = sqlconn()
        check = sql.session.execute(Select.user_exists_username_password(({"username":form.username._value(),"password":generate_hash(form.password._value())}))).mappings().fetchall()
        if len(check)>0:
            session["user"] = check[0]["id"]
            return redirect(url_for('home')),200
        else: 
            flash("You are a fraud")
            return render_template('login.html', form=form),401
    return render_template('login.html', form=form)

@app.route('/change-username', methods=['GET','POST'])
def change_username():
    if "user" not in session:
        return redirect(url_for('login'))
    form = UsernameForm()
    if form.validate_on_submit():
        with sqlconn() as sql:
            check = sql.session.execute(Select.user_unique_username({"username":escape(form.username._value())})).mappings().fetchall()
            if len(check)>0:
                flash("Username already exists")
                return redirect(url_for('home')),400
            sql.session.execute(Update.user_username({"id":session["user"],"username":escape(form.username._value())}))
            sql.session.commit()
            session.pop("username")
            flash("Success")
            return redirect(url_for('home')),200
    return render_template('username_change.html',form=form)

@app.route('/change-password', methods=['GET','POST'])
def change_password():
    if "user" not in session:
        return redirect(url_for('login'))
    form = ChangePasswordForm()
    if form.validate_on_submit():
        with sqlconn() as sql:
            check = sql.session.execute(Select.user_exists_id_password({"user_id":session["user"],
            "password":generate_hash(escape(form.current_password._value()))})).mappings().fetchall()
            if len(check)==0:
                flash("Current password is wrong")
                return redirect(url_for('home')),400
            sql.session.execute(Update.user_password({"user_id":session["user"],"password":generate_hash(escape(form.new_password._value()))}))
            sql.session.commit()
            flash("Success")
            return redirect(url_for('home')),200
    return render_template('password_change.html',form=form)
        
@app.route('/set-password', methods=['GET','POST'])
def set_password():
    if "user" not in session:
        return redirect(url_for('login'))
    form = SetPasswordForm()
    if form.validate_on_submit():
        with sqlconn() as sql:
            check = sql.session.execute(Select.user_exists_id_none_password({"user_id":session["user"]})).mappings().fetchall()
            if len(check)==0:
                flash("This is only for the users registered with OAUTH2 methods.")
                return redirect(url_for('home')),400
            sql.session.execute(Update.user_password({"user_id":session["user"],"password":generate_hash(escape(form.new_password._value()))}))
            sql.session.commit()
            flash("Success")
            return redirect(url_for('home')),200
    return render_template('password_set.html',form=form)        

@app.route('/remove-account', methods=['GET','POST'])
def remove_account():
    if "user" not in session:
        return redirect(url_for('home'))
    form = UsernameForm()
    if form.validate_on_submit():
        with sqlconn() as sql:
            get_user = sql.session.execute(Select.user_username({"id":session["user"]})).mappings().fetchone()
            if "username" not in get_user:
                flash("Write your username correctly to delete your account.")
                return redirect(url_for('home')),400
            username = get_user["username"]
            if str(escape(form.username._value())) == username:
                get_user_pp_location = sql.session.execute(Select.user_profile_picture({"user":username})).mappings().fetchone()
                if get_user_pp_location["profile_picture"]:
                    try:
                        os.remove(project_dir+"/static/"+profile_photos_dir+get_user_pp_location["profile_picture"])
                    except FileNotFoundError:
                        pass
                sql.session.execute(Delete.user({"id":session["user"],"username":username}))
                sql.commit()
                session.pop('user', None)
                flash("Removed profile picture and all the info about you successfully.")
                return redirect(url_for('home')),200
    return render_template('remove-account.html',form=form)
                
            
@app.route('/logout',methods=['GET'])
def logout():
    if "user" in session:
        session.pop('user', None)
        session.pop('username',None)
        session.pop('picture',None)
    return redirect(url_for('home')),200

@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
    if "user" in session:
        with sqlconn() as sql:
            user_info = get_user_info(sql)
            user_scores = {
                "comment_count":sql.session.execute(Select.user_comment_count({"user_id":session["user"]})).mappings().fetchone()["count"],
                "post_count":sql.session.execute(Select.user_post_count({"user_id":session["user"]})).mappings().fetchone()["count"],
                "comment_karma":sql.session.execute(Select.user_karma_point_comment({"user_id":session["user"]})).mappings().fetchone()["sum"],
                "post_karma":sql.session.execute(Select.user_karma_point_post({"user_id":session["user"]})).mappings().fetchone()["sum"]
            }
            return render_template('home.html',user=user_info["username"], picture = profile_photos_dir+user_info["picture"]["profile_picture"],stats = user_scores)
    return render_template('home.html')

@app.route('/terms-of-service', methods=['GET'])
def terms_of_service():
    if "user" in session:
        with sqlconn() as sql:
            user_info = get_user_info(sql)
            return render_template('terms-of-service.html',user=user_info["username"])
    return render_template('terms-of-service.html')

@app.route('/privacy-policy', methods=['GET'])
def privacy_policy():
    if "user" in session:
        with sqlconn() as sql:
            user_info = get_user_info(sql)
            return render_template('privacy-policy.html',user=user_info["username"])
    return render_template('privacy-policy.html')

@app.route('/add-profile-picture', methods=['GET', 'POST'])
def add_profile_picture():
    form = AddProfilePicture()
    if request.method == "POST":
        if not form.validate_on_submit():
            flash("Only jpg files are allowed.")
            return """<script>window.close();</script>"""
        if "user" not in session:
            return redirect(url_for('login'))
        with sqlconn() as sql:
            user_info = get_user_info(sql)
            rand= "pp-"+str(uuid.uuid4())+".jpg"
            filepath = project_dir+"/static/"+profile_photos_dir+rand
            form.photo.data.save(filepath)
            try:
                img = Image.open(filepath)
                img.verify()
                img.close()
            except:
                os.remove(filepath)
                flash("This is not an image")
                return """<script>window.close();</script>""",400
            session.pop("picture")
            sql.session.execute(Update.user_profile_picture({"id":user_info["username"],"profile_picture":rand}))
            sql.commit()
            flash('Picture added successfully!')
            return """<script>window.close();window.opener.location.reload();</script>"""
    return render_template('add-profile-picture.html', form=form)

@app.route('/remove-profile-picture', methods=['GET'])
def remove_profile_picture():
    if "user" not in session:
        return redirect(url_for('login'))
    with sqlconn() as sql:
        user_info = get_user_info(sql)
        session.pop("picture")
        sql.session.execute(Update.user_profile_picture({"id":user_info["username"],"profile_picture":None}))
        sql.commit()
        flash('Picture removed successfully!')
        return redirect(url_for('home'))


def get_user_info(sql):
    user =  session["user"]
    if "username" not in session:
        user = sql.session.execute(Select.user_username({"id":user})).mappings().fetchone()
        if "username" in user:
            user = user["username"]
            session["username"] = user
        else:
            return("Error."),400
    else: user = session["username"]
    if "picture" not in session:
        picture = sql.session.execute(Select.user_profile_picture({"user":user})).mappings().fetchone()
        if picture["profile_picture"] is None:
            picture = {"profile_picture": "pp.jpg"}
        session["picture"] = {"profile_picture": picture["profile_picture"]}
    else: picture = session["picture"]

    return {"username":user,"picture":picture}

from app import comments_views,posts_views,forums_views,views_google_oauth2,views_facebook_oauth2