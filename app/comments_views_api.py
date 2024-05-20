from flask import  jsonify,request,escape
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import Comment, CommentLikes
from app.sql_dependant.sql_connection import sqlconn
from app.sql_dependant.sql_write import Delete, Update
from app.views_api import check_auth
from . import app
from app.helpers import listify

@app.route('/api/create/comment',methods=['POST'])
def api_create_comment():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    
    if not set(["post_id","content"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    post_id = escape(request.json["post_id"])
    comment_id = 0 if not set(["parent_id"]).issubset(set(request.json.keys())) else escape(request.json["parent_id"])

    with sqlconn() as sql:
        comment = Comment(
            user_id = auth_check["user"],
            parent_id = comment_id,
            post_id = post_id,
            content=escape(request.json["content"]))
        sql.session.add(comment)
        sql.session.commit()
        return jsonify({"msg":"Comment added successfully!"}),200

@app.route('/api/delete/comment',methods=['POST'])
def api_delete_comment():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    
    if not set(["comment_id"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    comment_id = escape(request.json["comment_id"])

    with sqlconn() as sql:
        check_comment_exists = sql.session.execute(Select.comment(comment_id)).mappings().fetchone()
        if not check_comment_exists:
            return jsonify({"msg":"You can't delete what doesn't exist."}),401
        
        if not (check_comment_exists["user_id"] == auth_check["user_id"]):
            return jsonify({"msg":"You can't delete a comment someone else created."}),401
        sql.session.execute(Delete.comment({"user_id":auth_check["user_id"],"comment_id":comment_id}))
        sql.session.commit()
        return jsonify({"msg":"Deleted comment"}),200

@app.route('/api/fetch/replies',methods=['POST'])
def api_fetch_replies():
    if not set(["parent_id","post_id"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    
    with sqlconn() as sql:
        replies = listify(sql.session.execute(Select.replies_of_comment({"post_id":escape(request.json["post_id"]),"parent_id":escape(request.json["parent_id"])})).mappings().fetchall())
        return jsonify({"replies":replies})


@app.route('/api/comment/like',methods=['POST'])
def api_like_comment():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    if not set(["comment_id"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    user_id = auth_check["user"]
    comment_id = escape(request.json["comment_id"])

    with sqlconn() as sql:
        check_l_d_exists = sql.session.execute(Select.commentlikes_exists({"user_id":user_id,"comment_id":comment_id})).mappings().fetchone()
        if check_l_d_exists:
            if check_l_d_exists["l_d"] == "Like":
                sql.session.execute(Delete.commentlikes({"user_id":user_id,"comment_id":comment_id,"l_d":"Like"}))
                sql.session.execute(Update.comment_user_dislike_comment({"comment_id":comment_id}))
                sql.session.commit()
                return jsonify({"msg":"Unliked"}),200
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
        return jsonify({"msg":"Liked"}),200

@app.route('/api/comment/dislike',methods=['POST'])
def api_dislike_comment():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    if not set(["comment_id"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    user_id = auth_check["user"]
    comment_id = escape(request.json["comment_id"])

    with sqlconn() as sql:
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
                return jsonify({"msg":"Undisliked"}),200
        like = CommentLikes(
            user_id = escape(user_id),
            comment_id = escape(comment_id),
            l_d = "Dislike"
        )
        sql.session.add(like)
        sql.session.execute(Update.comment_user_dislike_comment({"comment_id":comment_id}))
        sql.session.commit()
        return jsonify({"msg":"Disliked"}),200