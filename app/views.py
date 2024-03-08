import uuid

from app.flaskforms import  RegisterForm,LoginForm,AddProfilePicture, UsernameForm
from flask import  redirect, url_for,render_template,session,flash,request,escape
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import   User
from app.sql_dependant.sql_connection import sqlconn
from app.sql_dependant.sql_write import  Update
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
            email=form.email._value(),
            password=generate_hash(form.password._value()))
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
                return "Username already exists",400
            sql.session.execute(Update.user_username({"id":session["user"],"username":escape(form.username._value())}))
            sql.session.commit()
            flash("Success")
            return redirect(url_for('home')),200
    return render_template('username_change.html',form=form)
        

@app.route('/logout',methods=['GET'])
def logout():
    if "user" in session:
        session.pop('user', None)
    return redirect(url_for('home')),200

@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
    if "user" in session:
        user =  session["user"]
        with sqlconn() as sql:
            user = sql.session.execute(Select.user_username({"id":user})).mappings().fetchone()
            if "username" in user:
                user = user["username"]
            else:
                return("Error."),400
            picture = sql.session.execute(Select.user_profile_picture({"user":user})).mappings().fetchone()
            user_scores = {
                "comment_count":sql.session.execute(Select.user_comment_count({"user_id":session["user"]})).mappings().fetchone()["count"],
                "post_count":sql.session.execute(Select.user_post_count({"user_id":session["user"]})).mappings().fetchone()["count"],
                "comment_karma":sql.session.execute(Select.user_karma_point_comment({"user_id":session["user"]})).mappings().fetchone()["sum"],
                "post_karma":sql.session.execute(Select.user_karma_point_post({"user_id":session["user"]})).mappings().fetchone()["sum"]
            }
            if picture["profile_picture"] is None:
                picture = {"profile_picture": "pp.jpg"}
            return render_template('home.html',user=user, picture = profile_photos_dir+picture["profile_picture"],stats = user_scores)
    return render_template('home.html')

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
            user = sql.session.execute(Select.user_username({"id":session["user"]})).mappings().fetchone()
            if "username" in user:
                user = user["username"]
            else:
                return("Error."),400
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
            sql.session.execute(Update.user_profile_picture({"id":user,"profile_picture":rand}))
            sql.commit()
            flash('Picture added successfully!')
            return """<script>window.close();window.opener.location.reload();</script>"""
    return render_template('add-profile-picture.html', form=form)

@app.route('/remove-profile-picture', methods=['GET'])
def remove_profile_picture():
    if "user" not in session:
        return redirect(url_for('login'))
    with sqlconn() as sql:
        user = sql.session.execute(Select.user_username({"id":session["user"]})).mappings().fetchone()
        if "username" in user:
            user = user["username"]
        else:
            return("Error."),400
        sql.session.execute(Update.user_profile_picture({"id":user,"profile_picture":None}))
        sql.commit()
        flash('Picture removed successfully!')
        return redirect(url_for('home'))


from app import comments_views,posts_views,forums_views,views_google_oauth2