
from flask import  jsonify,request,escape
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import  Forum
from app.sql_dependant.sql_connection import sqlconn
from app.views_api import check_auth
from . import app
from app.helpers import listify

@app.route('/api/forum',methods=['POST'])
def api_forum_page():
    id = 0
    if "id" in request.json:
        id = int(request.json["id"])
    pagenumber = 0
    if "page" in request.json:
        pagenumber = int(request.json["page"])
    with sqlconn() as sql:
        contents = sql.session.execute(Select.forum_page(id)).mappings().fetchone()
        posts = listify(sql.session.execute(Select.posts({"id":id,"page":pagenumber})).mappings().fetchall())
        for post in posts:
            post["link"] = "post?id="+str(post["id"])
        postcount = sql.session.execute(Select.posts_count(id)).mappings().fetchone()
        postcount = (postcount["count"]-1)//10
        return jsonify({"msg":"","contents":contents,"posts":posts,"postcount":postcount}),200

@app.route('/api/forums', methods=['POST'])
def api_forums_page():
    pagenumber = 0
    if "page" in request.json:
        pagenumber = int(request.json["page"])
    with sqlconn() as sql:
        forums = listify(sql.session.execute(Select.forums(pagenumber)).mappings().fetchall())
        for forum in forums:
            forum["link"] = "forum?id="+str(forum["id"])
        forumcount = sql.session.execute(Select.forums_count()).mappings().fetchone()
        forumcount = (forumcount["count"]-1)//5
        return jsonify({"msg":"","forums":forums,"page_count":forumcount}),200

@app.route('/api/create/forum',methods=['POST'])
def api_create_forum():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    
    if not set(["name","description"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    
    with sqlconn() as sql:
        forum = Forum(
            name=escape(request.json["name"]),
            description=escape(request.json["description"]))
        check = sql.session.execute(Select.forum_exists(escape(request.json["name"]))).mappings().fetchall()
        if len(check)>0:
            return jsonify({"msg":"Forum with this name already exists"}),400
        sql.session.add(forum)
        sql.session.commit()
        return jsonify({"msg":"Forum added successfully!"}),200