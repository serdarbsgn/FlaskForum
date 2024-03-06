from app.flaskforms import CreateCommentForm
from flask import  redirect, url_for,render_template,session,flash,request,escape
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import Comment, CommentLikes
from app.sql_dependant.sql_connection import sqlconn
from app.sql_dependant.sql_write import Delete, Update
from . import app
from app.helpers import listify

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

@app.route('/fetch/replies',methods=['GET'])
def fetch_replies():
    if request.args.get("postid") and request.args.get("commentid"):
        parent_id = request.args.get("commentid",0,type=int)
        post_id = request.args.get("postid",0,type=int)
    sql = sqlconn()
    replies = listify(sql.session.execute(Select.replies_of_comment({"post_id":post_id,"parent_id":parent_id})).mappings().fetchall())
    sql.close()
    return replies


@app.route('/comment/like',methods=['GET'])
def like_comment():
    if "user" not in session:
        flash("Log in first")
        return """"<script>window.reload();""",401
    if request.args.get("commentid"):
        user_id = session["user"]
        comment_id = request.args.get("commentid",0,type=int)
    if type(user_id) is not int and type(comment_id) is not int:
        flash("Failed to like")
        return "Failed to like",401
    sql = sqlconn()
    check_l_d_exists = sql.session.execute(Select.commentlikes_exists({"user_id":user_id,"comment_id":comment_id})).mappings().fetchone()
    if check_l_d_exists:
        if check_l_d_exists["l_d"] == "Like":
            sql.session.execute(Delete.commentlikes({"user_id":user_id,"comment_id":comment_id,"l_d":"Like"}))
            sql.session.execute(Update.comment_user_dislike_comment({"comment_id":comment_id}))
            sql.session.commit()
            flash("Unliked")
            sql.close()
            return """<script>window.reload();</script>""",200
        elif check_l_d_exists["l_d"] == "Dislike":
            sql.session.execute(Delete.commentlikes({"user_id":user_id,"comment_id":comment_id,"l_d":"Dislike"}))
            sql.session.execute(Update.comment_user_like_comment({"comment_id":comment_id}))
            sql.session.commit()
    like = CommentLikes(
        user_id = escape(user_id),
        comment_id = escape(comment_id),
        l_d = "Like"
    )
    sql.session.add(like)
    sql.session.execute(Update.comment_user_like_comment({"comment_id":comment_id}))
    sql.session.commit()
    flash("Liked")
    sql.close()
    return """<script>window.reload();</script>""",200

@app.route('/comment/dislike',methods=['GET'])
def dislike_comment():
    if "user" not in session:
        flash("Log in first")
        return """"<script>window.reload();""",401
    if "user" in session and request.args.get("commentid"):
        user_id = session["user"]
        comment_id = request.args.get("commentid",0,type=int)
    if type(user_id) is not int and type(comment_id) is not int:
        flash("Failed to dislike")
        return """<script>window.reload();""",401
    sql = sqlconn()
    check_l_d_exists = sql.session.execute(Select.commentlikes_exists({"user_id":user_id,"comment_id":comment_id})).mappings().fetchone()
    if check_l_d_exists:
        if check_l_d_exists["l_d"] == "Like":
            sql.session.execute(Delete.commentlikes({"user_id":user_id,"comment_id":comment_id,"l_d":"Like"}))
            sql.session.execute(Update.comment_user_dislike_comment({"comment_id":comment_id}))
            sql.session.commit()
        elif check_l_d_exists["l_d"] == "Dislike":
            sql.session.execute(Delete.commentlikes({"user_id":user_id,"comment_id":comment_id,"l_d":"Dislike"}))
            sql.session.execute(Update.comment_user_like_comment({"comment_id":comment_id}))
            sql.session.commit()
            flash("Undisliked")
            sql.close()
            return """<script>window.reload();</script>""",200
    like = CommentLikes(
        user_id = escape(user_id),
        comment_id = escape(comment_id),
        l_d = "Dislike"
    )
    sql.session.add(like)
    sql.session.execute(Update.comment_user_dislike_comment({"comment_id":comment_id}))
    sql.session.commit()
    flash("Disliked")
    sql.close()
    return """<script>window.reload();</script>""",200