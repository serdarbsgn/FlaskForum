
from app.flaskforms import  CreateForumForm
from flask import  redirect, url_for,render_template,session,flash,request,escape
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import  Forum
from app.sql_dependant.sql_connection import sqlconn
from . import app
from app.helpers import listify,profile_photos_dir

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