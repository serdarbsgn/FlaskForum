from flask import jsonify,escape,request
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import  Post, PostLikes
from app.sql_dependant.sql_connection import sqlconn
from app.sql_dependant.sql_write import Update,Delete
from app.views_api import check_auth
from . import app
from app.helpers import listify

@app.route('/api/post',methods = ['POST'])
def api_post_page():
    id = 0
    if "id" in request.json:
        id = int(request.json["id"])
    pagenumber = 0
    if "page" in request.json:
        pagenumber = int(request.json["page"])
    with sqlconn() as sql:
        contents = sql.session.execute(Select.post_page(id)).mappings().fetchone()
        if not contents:
            return jsonify({"msg":"This post doesn't exist"}),404
        comments = listify(sql.session.execute(Select.comments({"id":id,"page":pagenumber})).mappings().fetchall())
        comment_count = sql.session.execute(Select.comments_count(id)).mappings().fetchone()
        comment_count = (comment_count["count"]-1)//20
        created_by = sql.session.execute(Select.user_username({"id":contents["user_id"]})).mappings().fetchone()["username"]
        return jsonify({"contents":contents,"created_by":created_by,"comments":comments,"comment_count":comment_count}),200

@app.route('/api/create/post',methods=['POST'])
def api_create_post():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    
    if not set(["forum_id","title","content"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    
    with sqlconn() as sql:
        post = Post(
            user_id = auth_check["user"],
            forum_id = escape(request.json["forum_id"]),
            title=escape(request.json["title"]),
            content=escape(request.json["content"]))
        sql.session.add(post)
        sql.session.commit()
        return jsonify({"msg":"Post added successfully!"}),200

@app.route('/api/update/post',methods=['POST'])
def api_update_post():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    
    if not set(["post_id","title","content"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400

    with sqlconn() as sql:
        sql.session.execute(Update.post({"user_id":auth_check["user"],"post_id":escape(request.json["post_id"]),
                                        "title":escape(request.json["title"]),"content":escape(request.json["content"])}))
        sql.session.commit()
    return jsonify({"msg":"Post updated successfully!"}),200

@app.route('/api/delete/post',methods=['POST'])
def api_delete_post():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    
    if not set(["post_id"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400

    with sqlconn() as sql:
        check_post_exists = sql.session.execute(Select.post_page(escape(request.json["post_id"]))).mappings().fetchone()
        if not check_post_exists:
            return jsonify({"msg":"You can't delete what doesn't exist."}),400
        if not (check_post_exists["user_id"] == auth_check["user"]):
            return jsonify({"msg":"You can't delete a post someone else created."}),401
        sql.session.execute(Delete.post({"user_id":auth_check["user"],"post_id":escape(request.json["post_id"])}))
        sql.session.commit()
        return jsonify({"msg":"Deleted post"}),200

@app.route('/api/post/like',methods=['POST'])
def api_like_post():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    
    if not set(["post_id"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    post_id = escape(request.json["post_id"])

    with sqlconn() as sql:
        check_l_d_exists = sql.session.execute(Select.postlikes_exists({"user_id":auth_check["user"],"post_id":post_id})).mappings().fetchone()
        if check_l_d_exists:
            if check_l_d_exists["l_d"] == "Like":
                sql.session.execute(Delete.postlikes({"user_id":auth_check["user"],"post_id":post_id,"l_d":"Like"}))
                sql.session.execute(Update.post_user_dislike_post({"post_id":post_id}))
                sql.session.commit()
                return jsonify({"msg":"Unliked"}),200
            elif check_l_d_exists["l_d"] == "Dislike":
                sql.session.execute(Delete.postlikes({"user_id":auth_check["user"],"post_id":post_id,"l_d":"Dislike"}))
                sql.session.execute(Update.post_user_like_post({"post_id":post_id}))
                sql.session.commit()
        like = PostLikes(
            user_id = escape(auth_check["user"]),
            post_id = escape(post_id),
            l_d = "Like"
        )
        sql.session.add(like)
        sql.session.execute(Update.post_user_like_post({"post_id":post_id}))
        sql.session.commit()
        return jsonify({"msg":"Liked"}),200

@app.route('/api/post/dislike',methods=['POST'])
def api_dislike_post():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    
    if not set(["post_id"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    post_id = escape(request.json["post_id"])

    with sqlconn() as sql:
        check_l_d_exists = sql.session.execute(Select.postlikes_exists({"user_id":auth_check["user"],"post_id":post_id})).mappings().fetchone()
        if check_l_d_exists:
            if check_l_d_exists["l_d"] == "Like":
                sql.session.execute(Delete.postlikes({"user_id":auth_check["user"],"post_id":post_id,"l_d":"Like"}))
                sql.session.execute(Update.post_user_dislike_post({"post_id":post_id}))
                sql.session.commit()
            elif check_l_d_exists["l_d"] == "Dislike":
                sql.session.execute(Delete.postlikes({"user_id":auth_check["user"],"post_id":post_id,"l_d":"Dislike"}))
                sql.session.execute(Update.post_user_like_post({"post_id":post_id}))
                sql.session.commit()
                return jsonify({"msg":"Undisliked"}),200
        like = PostLikes(
            user_id = escape(auth_check["user"]),
            post_id = escape(post_id),
            l_d = "Dislike"
        )
        sql.session.add(like)
        sql.session.execute(Update.post_user_dislike_post({"post_id":post_id}))
        sql.session.commit()
        return jsonify({"msg":"Disliked"}),200