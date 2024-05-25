from app.flaskforms import  CreatePostForm, UpdatePostForm
from flask import redirect, url_for,render_template,escape,flash,request,session
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import  Post, PostLikes
from app.sql_dependant.sql_connection import sqlconn
from app.sql_dependant.sql_write import Update,Delete
from app.views import get_user_info
from . import app
from app.helpers import listify,profile_photos_dir

@app.route('/post',methods = ['GET'])
def post_page():
    id = 0
    if request.args.get("id"):
        id = request.args.get("id",0,type=int)
    pagenumber = 0
    if request.args.get("page"):
        pagenumber = request.args.get("page",0,type=int)
    with sqlconn() as sql:
        contents = sql.session.execute(Select.post_page(id)).mappings().fetchone()
        if not contents:
            return "This post doesn't exist",404
        comments = listify(sql.session.execute(Select.comments({"id":id,"page":pagenumber})).mappings().fetchall())
        comment_count = sql.session.execute(Select.comments_count(id)).mappings().fetchone()
        comment_count = (comment_count["count"]-1)//20
        created_by = sql.session.execute(Select.user_username({"id":contents["user_id"]})).mappings().fetchone()["username"]
        if "user" in session:
            user_info = get_user_info(sql)
            return render_template('post.html',user=user_info["username"],picture = profile_photos_dir+user_info["picture"]["profile_picture"],contents = contents,created_by = created_by,comments=comments,comment_count=comment_count,hide_header = request.args.get('hide_header',0,type=int))
        return render_template('post.html',contents = contents,created_by = created_by,comments=comments,comment_count=comment_count,hide_header = request.args.get('hide_header',0,type=int))

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
        with sqlconn() as sql:
            post = Post(
                user_id = session["user"],
                forum_id = escape(form.forum_id._value()),
                title=escape(form.title._value()),
                content=escape(form.content._value()))
            sql.session.add(post)
            sql.session.commit()
            flash('Post added successfully!')
            return """<script>window.close();window.opener.location.reload();</script>"""
    return render_template('create_post.html', form=form,forumid=forumid)

@app.route('/update/post',methods=['GET','POST'])
def update_post():
    if request.args.get("postid"):
        postid = request.args.get("postid",type=int)
        with sqlconn() as sql:
            original_post = sql.session.execute(Select.post_page(postid)).mappings().fetchone()
            form = UpdatePostForm(post_id = postid,title = original_post["title"],content = original_post["content"])
    if "post_id" in request.form:
        form = UpdatePostForm(post_id = int(request.form["post_id"]))
    if form.validate_on_submit():
        if "user" not in session:
            return redirect(url_for('login'))
        with sqlconn() as sql:
            sql.session.execute(Update.post({"user_id":session["user"],"post_id":escape(form.post_id._value()),
                                            "title":escape(form.title._value()),"content":escape(form.content._value())}))
            sql.session.commit()
        flash("Updated")
        return """<script>window.close();window.opener.location.reload();</script>"""
    return render_template('update_post.html', form=form,postid=postid)


@app.route('/delete/post',methods=['GET'])
def delete_post():
    if "user" not in session:
        flash("Log in first")
        return """<script>window.reload();""",401
    if request.args.get("postid"):
        user_id = session["user"]
        post_id = request.args.get("postid",0,type=int)
    if type(user_id) is not int and type(post_id) is not int:
        flash("Failed to delete")
        return "Failed to delete",401
    with sqlconn() as sql:
        check_post_exists = sql.session.execute(Select.post_page(post_id)).mappings().fetchone()
        if not check_post_exists:
            flash("Failed to delete")
            return "Failed to delete",401
        if not (check_post_exists["user_id"] == user_id):
            flash("Can't delete a post someone else created.")
            return "Can't delete a post someone else created.",401
        sql.session.execute(Delete.post({"user_id":user_id,"post_id":post_id}))
        sql.session.commit()
        flash("Deleted post")
        return "Deleted post",200

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
    with sqlconn() as sql:
        check_l_d_exists = sql.session.execute(Select.postlikes_exists({"user_id":user_id,"post_id":post_id})).mappings().fetchone()
        if check_l_d_exists:
            if check_l_d_exists["l_d"] == "Like":
                sql.session.execute(Delete.postlikes({"user_id":user_id,"post_id":post_id,"l_d":"Like"}))
                sql.session.execute(Update.post_user_dislike_post({"post_id":post_id}))
                sql.session.commit()
                flash("Unliked")
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
    with sqlconn() as sql:
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
        return """<script>window.reload();""",200