from app.flaskforms import  CreatePostForm, UpdatePostForm
from flask import redirect, url_for,render_template,session,flash,request,escape
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import  Post, PostLikes
from app.sql_dependant.sql_connection import sqlconn
from app.sql_dependant.sql_write import Update,Delete
from . import app
from app.helpers import listify

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
    comment_count = (comment_count["count"]-1)//20
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

@app.route('/update/post',methods=['GET','POST'])
def update_post():
    if request.args.get("postid"):
        postid = request.args.get("postid",type=int)
        sql = sqlconn()
        original_post = sql.session.execute(Select.post_page(postid)).mappings().fetchone()
        sql.close()
        form = UpdatePostForm(post_id = postid,title = original_post["title"],content = original_post["content"])
    if "post_id" in request.form:
        form = UpdatePostForm(post_id = int(request.form["post_id"]))
    if form.validate_on_submit():
        if "user" not in session:
            return redirect(url_for('login'))
        sql = sqlconn()
        sql.session.execute(Update.post({"user_id":session["user"],"post_id":escape(form.post_id._value()),
                                         "title":escape(form.title._value()),"content":escape(form.content._value())}))
        sql.session.commit()
        sql.close()
        flash("Updated")
        return """<script>window.close();window.opener.location.reload();</script>"""
    return render_template('update_post.html', form=form,postid=postid)


@app.route('/post/like',methods=['GET'])
def like_post():
    if "user" not in session:
        flash("Log in first")
        return """<script>window.reload();""",401
    if request.args.get("postid"):
        user_id = session["user"]
        post_id = request.args.get("postid",0,type=int)
    if type(user_id) is not int and type(post_id) is not int:
        flash("Failed to like")
        return "Failed to like",401
    sql = sqlconn()
    check_l_d_exists = sql.session.execute(Select.postlikes_exists({"user_id":user_id,"post_id":post_id})).mappings().fetchone()
    if check_l_d_exists:
        if check_l_d_exists["l_d"] == "Like":
            sql.session.execute(Delete.postlikes({"user_id":user_id,"post_id":post_id,"l_d":"Like"}))
            sql.session.execute(Update.post_user_dislike_post({"post_id":post_id}))
            sql.session.commit()
            flash("Unliked")
            sql.close()
            return """<script>window.reload();""",200
        elif check_l_d_exists["l_d"] == "Dislike":
            sql.session.execute(Delete.postlikes({"user_id":user_id,"post_id":post_id,"l_d":"Dislike"}))
            sql.session.execute(Update.post_user_like_post({"post_id":post_id}))
            sql.session.commit()
    like = PostLikes(
        user_id = escape(user_id),
        post_id = escape(post_id),
        l_d = "Like"
    )
    sql.session.add(like)
    sql.session.execute(Update.post_user_like_post({"post_id":post_id}))
    sql.session.commit()
    flash("Liked")
    sql.close()
    return """<script>window.reload();""",200

@app.route('/post/dislike',methods=['GET'])
def dislike_post():
    if "user" not in session:
        flash("Log in first")
        return """<script>window.reload();""",401
    if "user" in session and request.args.get("postid"):
        user_id = session["user"]
        post_id = request.args.get("postid",0,type=int)
    if type(user_id) is not int and type(post_id) is not int:
        flash("Failed to dislike")
        return """<script>window.reload();""",401
    sql = sqlconn()
    check_l_d_exists = sql.session.execute(Select.postlikes_exists({"user_id":user_id,"post_id":post_id})).mappings().fetchone()
    if check_l_d_exists:
        if check_l_d_exists["l_d"] == "Like":
            sql.session.execute(Delete.postlikes({"user_id":user_id,"post_id":post_id,"l_d":"Like"}))
            sql.session.execute(Update.post_user_dislike_post({"post_id":post_id}))
            sql.session.commit()
        elif check_l_d_exists["l_d"] == "Dislike":
            sql.session.execute(Delete.postlikes({"user_id":user_id,"post_id":post_id,"l_d":"Dislike"}))
            sql.session.execute(Update.post_user_like_post({"post_id":post_id}))
            sql.session.commit()
            flash("Undisliked")
            sql.close()
            return """<script>window.reload();""",200
    like = PostLikes(
        user_id = escape(user_id),
        post_id = escape(post_id),
        l_d = "Dislike"
    )
    sql.session.add(like)
    sql.session.execute(Update.post_user_dislike_post({"post_id":post_id}))
    sql.session.commit()
    flash("Disliked")
    sql.close()
    return """<script>window.reload();""",200