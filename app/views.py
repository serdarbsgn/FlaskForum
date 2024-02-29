from asyncio import sleep
import uuid
from app.flaskforms import CreateCommentForm, CreateForumForm, CreatePostForm, RegisterForm,LoginForm,AddProfilePicture
from flask import jsonify, redirect, url_for,render_template,session,flash,request,escape
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import Comment, Forum, Post, User
from app.sql_dependant.sql_connection import sqlconn
from app.sql_dependant.sql_write import Update
from app.utils import generate_hash
from PIL import Image
from . import app
import os
project_dir = os.path.dirname(os.path.abspath(__file__))
profile_photos_dir = "/photos/users/"
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=escape(form.username._value()),
            email=form.email._value(),
            password=generate_hash(form.password._value()))
        sql = sqlconn()
        check = sql.session.execute(Select.user_unique_username_email({"username":user.username,"email":user.email})).mappings().fetchall()
        if len(check)>0:
            sql.close()
            return "Email and/or Username already exists",400
        sql.session.add(user)
        sql.session.commit()
        sql.close()
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
        sql = sqlconn()
        user = sql.session.execute(Select.user_username({"id":user})).mappings().fetchone()
        if "username" in user:
            user = user["username"]
        else:
            sql.close()
            return("Error."),400
        picture = sql.session.execute(Select.user_profile_picture({"user":user})).mappings().fetchone()
        if picture["profile_picture"] is None:
            picture = {"profile_picture": "pp.jpg"}
        sql.close()
        return render_template('home.html',user=user, picture = profile_photos_dir+picture["profile_picture"])
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
        sql = sqlconn()
        user = sql.session.execute(Select.user_username({"id":session["user"]})).mappings().fetchone()
        if "username" in user:
            user = user["username"]
        else:
            sql.close()
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
            sql.close()
            flash("This is not an image")
            return """<script>window.close();</script>""",400
        sql.session.execute(Update.user_profile_picture({"id":user,"profile_picture":rand}))
        sql.commit()
        sql.close()
        flash('Picture added successfully!')
        return """<script>window.close();window.opener.location.reload();</script>"""
    return render_template('add-profile-picture.html', form=form)

@app.route('/remove-profile-picture', methods=['GET'])
def remove_profile_picture():
    if "user" not in session:
        return redirect(url_for('login'))
    sql = sqlconn()
    user = sql.session.execute(Select.user_username({"id":session["user"]})).mappings().fetchone()
    if "username" in user:
        user = user["username"]
    else:
        sql.close()
        return("Error."),400
    sql.session.execute(Update.user_profile_picture({"id":user,"profile_picture":None}))
    sql.commit()
    sql.close()
    flash('Picture removed successfully!')
    return redirect(url_for('home'))

@app.route('/refresh-home', methods=['GET'])
def refresh():
    sleep(1)
    return redirect(url_for('home')),200

@app.route('/forum',methods=['GET'])
def forum_page():
    id = 0
    if request.args.get("id"):
        id = request.args.get("id",0,type=int)
    pagenumber = 0
    if request.args.get("page"):
        pagenumber = request.args.get("page",0,type=int)
    sql = sqlconn()
    contents = sql.session.execute(Select.forum_page(id)).mappings().fetchone()
    posts = listify(sql.session.execute(Select.posts({"id":id,"page":pagenumber})).mappings().fetchall())
    for post in posts:
        post["link"] = "post?id="+str(post["id"])
    postcount = sql.session.execute(Select.posts_count(id)).mappings().fetchone()
    postcount = (postcount["count"]-1)//10
    if "user" in session:
        user = sql.session.execute(Select.user_username({"id":session["user"]})).mappings().fetchone()
        if "username" in user:
            user = user["username"]
        picture = sql.session.execute(Select.user_profile_picture({"user":user})).mappings().fetchone()
        if picture["profile_picture"] is None:
            picture = {"profile_picture": "pp.jpg"}
        sql.close()
        return render_template('forum.html',user=user,contents = contents,posts = posts,postcount=postcount)
    sql.close()
    return render_template('forum.html',contents = contents,posts = posts,postcount=postcount)

@app.route('/post',methods = ['GET'])
def post_page():
    id = 0
    if request.args.get("id"):
        id = request.args.get("id",0,type=int)
    pagenumber = 0
    if request.args.get("page"):
        pagenumber = request.args.get("page",0,type=int)
    sql = sqlconn()
    contents = sql.session.execute(Select.post_page(id)).mappings().fetchone()
    comments = listify(sql.session.execute(Select.comments({"id":id,"page":pagenumber})).mappings().fetchall())
    comment_count = sql.session.execute(Select.comments_count(id)).mappings().fetchone()
    comment_count = (comment_count["count"]-1)//100
    created_by = sql.session.execute(Select.user_username({"id":contents["user_id"]})).mappings().fetchone()["username"]
    if "user" in session:
        user = sql.session.execute(Select.user_username({"id":session["user"]})).mappings().fetchone()
        if "username" in user:
            user = user["username"]
        picture = sql.session.execute(Select.user_profile_picture({"user":user})).mappings().fetchone()
        if picture["profile_picture"] is None:
            picture = {"profile_picture": "pp.jpg"}
        sql.close()
        return render_template('post.html',user=user,contents = contents,created_by = created_by,comments=comments,comment_count=comment_count)
    sql.close()
    return render_template('post.html',contents = contents,created_by = created_by,comments=comments,comment_count=comment_count)

@app.route('/forums', methods=['GET'])
def forums_page():
    pagenumber = 0
    if request.args.get("page"):
        pagenumber = request.args.get("page",0,type=int)
    sql = sqlconn()
    forums = listify(sql.session.execute(Select.forums(pagenumber)).mappings().fetchall())
    for forum in forums:
        forum["link"] = "forum?id="+str(forum["id"])
    forumcount = sql.session.execute(Select.forums_count()).mappings().fetchone()
    forumcount = (forumcount["count"]-1)//5
    if "user" in session:
        user = sql.session.execute(Select.user_username({"id":session["user"]})).mappings().fetchone()
        if "username" in user:
            user = user["username"]
        picture = sql.session.execute(Select.user_profile_picture({"user":user})).mappings().fetchone()
        if picture["profile_picture"] is None:
            picture = {"profile_picture": "pp.jpg"}
        sql.close()
        return render_template('forums.html',forums = forums,user=user,page_count=forumcount,picture = profile_photos_dir+picture["profile_picture"])
    sql.close()
    return render_template('forums.html',forums = forums,page_count=forumcount)

@app.route('/create/forum',methods=['GET','POST'])
def create_forum():
    form = CreateForumForm()
    if form.validate_on_submit():
        if "user" not in session:
            return redirect(url_for('login'))
        sql = sqlconn()
        user = sql.session.execute(Select.user_username({"id":session["user"]})).mappings().fetchone()
        if "username" in user:
            user = user["username"]
        else:
            sql.close()
            return("Error."),400
        forum = Forum(
            name=escape(form.name._value()),
            description=escape(form.description._value()))
        check = sql.session.execute(Select.forum_exists(form.name._value())).mappings().fetchall()
        if len(check)>0:
            sql.close()
            return "Forum with this name already exists",400
        sql.session.add(forum)
        sql.session.commit()
        sql.close()
        flash('Forum added successfully!')
        return """<script>window.close();window.opener.location.reload();</script>"""
    return render_template('create_forum.html', form=form)

@app.route('/create/post',methods=['GET','POST'])
def create_post():
    if request.args.get("forumid"):
        forumid = request.args.get("forumid",type=int)
        form = CreatePostForm(forum_id = forumid)
    if "forum_id" in request.form:
        form = CreatePostForm(forum_id = int(request.form["forum_id"]))
    if form.validate_on_submit():
        if "user" not in session:
            return redirect(url_for('login'))
        sql = sqlconn()
        post = Post(
            user_id = session["user"],
            forum_id = escape(form.forum_id._value()),
            title=escape(form.title._value()),
            content=escape(form.content._value()))
        sql.session.add(post)
        sql.session.commit()
        sql.close()
        flash('Post added successfully!')
        return """<script>window.close();window.opener.location.reload();</script>"""
    return render_template('create_post.html', form=form,forumid=forumid)

@app.route('/create/comment',methods=['GET','POST'])
def create_comment():
    if request.args.get("postid"):
        postid = request.args.get("postid",type=int)
        if request.args.get("commentid"):
            commentid = request.args.get("commentid",type=int)
        else: commentid = 0
        form = CreateCommentForm(post_id = postid,comment_id = commentid)
    if "post_id" in request.form and "comment_id" in request.form:
        form = CreateCommentForm(post_id = int(request.form["post_id"]),comment_id = int(request.form["comment_id"]))
    if form.validate_on_submit():
        if "user" not in session:
            return redirect(url_for('login'))
        sql = sqlconn()
        comment = Comment(
            user_id = session["user"],
            parent_id = form.comment_id._value(),
            post_id =escape(form.post_id._value()),
            content=escape(form.content._value()))
        sql.session.add(comment)
        sql.session.commit()
        sql.close()
        flash('Comment added successfully!')
        return """<script>window.close();window.opener.location.reload();</script>"""
    return render_template('create_comment.html', form=form,postid=postid,commentid=commentid)

def redirect(link):
    return '<script>window.location.href = "'+link+'";</script>'

def open_window(link):
    return '<script>window.open("'+link+'", "newwindow", "height=300,width=500");</script>'

def listify(map):
    templist = []
    for row in map:
        dicx = {}
        for key,val in row.items():
            dicx[key] = val
        templist.append(dicx)
    return templist