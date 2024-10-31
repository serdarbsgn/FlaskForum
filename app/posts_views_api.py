from datetime import datetime
from html import escape
from fastapi import HTTPException, Request
from pydantic import BaseModel, Field
from helpers import limit_line_breaks
from sql_dependant.sql_read import Select
from sql_dependant.sql_tables import  Post, PostLikes
from sql_dependant.sql_connection import sqlconn
from sql_dependant.sql_write import Update,Delete
from views_api import MsgResponse, check_auth
from main import app

class PostCommentsResponse(BaseModel):
    id : int
    parent_id : int
    username : str
    content : str
    likes : int
    created_at : datetime
    updated_at : datetime
    has_replies : bool

class PostContentsResponse(BaseModel):
    id : int
    forum_id : int
    user_id : int
    title : str
    content : str
    likes : int
    created_at : datetime
    updated_at : datetime

class PostPageResponse(BaseModel):
    contents:PostContentsResponse
    created_by:str

@app.get('/api/post/{post_id}',responses={
        200: {
            "description": "Success response",
            "model": PostPageResponse
        }})
async def api_post_page(post_id:int):
    id = post_id
    with sqlconn() as sql:
        contents = sql.session.execute(Select.post_page(id)).mappings().fetchone()
        if not contents:
            raise HTTPException(status_code=400, detail="This post doesn't exist")
        created_by = sql.session.execute(Select.user_username({"id":contents["user_id"]})).mappings().fetchone()["username"]
        return PostPageResponse(contents = contents,
                                created_by = created_by)
    
class CreatePostInfo(BaseModel):
    forum_id : int
    title : str = Field(min_length=4)
    content : str = Field(min_length=4)

@app.post('/api/post')
async def api_create_post(request:Request,create_post_info:CreatePostInfo):
    auth_check = check_auth(request)
    forum_id = create_post_info.forum_id
    title=escape(create_post_info.title)
    content=limit_line_breaks(escape(create_post_info.content),63)
    with sqlconn() as sql:
        post = Post(
            user_id = auth_check["user"],
            forum_id = forum_id,
            title=title,
            content=content)
        sql.session.add(post)
        sql.session.commit()
        return MsgResponse(msg="Post added successfully!")
    
class UpdatePostInfo(BaseModel):
    post_id : int
    title : str = Field(min_length=4)
    content : str = Field(min_length=4)

@app.put('/api/post')
async def api_update_post(request:Request,update_post_info:UpdatePostInfo):
    auth_check = check_auth(request)
    post_id = update_post_info.post_id
    title=escape(update_post_info.title)
    content=limit_line_breaks(escape(update_post_info.content),63)
    with sqlconn() as sql:
        sql.session.execute(Update.post({"user_id":auth_check["user"],"post_id":post_id,
                                        "title":title,"content":content}))
        sql.session.commit()
    return MsgResponse(msg="Post updated successfully!")

class DLDPostInfo(BaseModel):
    post_id : int

@app.delete('/api/post')
async def api_delete_post(request:Request,delete_post_info:DLDPostInfo):
    auth_check = check_auth(request)
    post_id = delete_post_info.post_id
    with sqlconn() as sql:
        check_post_exists = sql.session.execute(Select.post_page(post_id)).mappings().fetchone()
        if not check_post_exists:
            raise HTTPException(status_code=404, detail="You can't delete what doesn't exist.")
        if not (check_post_exists["user_id"] == auth_check["user"]):
            raise HTTPException(status_code=401, detail="You can't delete a post someone else created.")
        sql.session.execute(Delete.post({"user_id":auth_check["user"],"post_id":escape(request.json["post_id"])}))
        sql.session.commit()
        return MsgResponse(msg="Deleted post")

@app.post('/api/post/like')
async def api_like_post(request:Request,like_post_info:DLDPostInfo):
    auth_check = check_auth(request)
    post_id = like_post_info.post_id

    with sqlconn() as sql:
        def add_like():
            like = PostLikes(
                user_id = auth_check["user"],
                post_id = post_id,
                l_d = "Like"
            )
            sql.session.add(like)
            sql.session.execute(Update.post_user_like_post({"post_id":post_id}))
            sql.session.commit()
        check_l_d_exists = sql.session.execute(Select.postlikes_exists({"user_id":auth_check["user"],"post_id":post_id})).mappings().fetchone()
        if check_l_d_exists:
            if check_l_d_exists["l_d"] == "Like":
                sql.session.execute(Delete.postlikes({"user_id":auth_check["user"],"post_id":post_id,"l_d":"Like"}))
                sql.session.execute(Update.post_user_dislike_post({"post_id":post_id}))
                sql.session.commit()
                return MsgResponse(msg="Unliked")
            elif check_l_d_exists["l_d"] == "Dislike":
                sql.session.execute(Delete.postlikes({"user_id":auth_check["user"],"post_id":post_id,"l_d":"Dislike"}))
                sql.session.execute(Update.post_user_like_post({"post_id":post_id}))
                sql.session.commit()
                add_like()
                return MsgResponse(msg="Liked2")
        add_like()
        return MsgResponse(msg="Liked")

@app.post('/api/post/dislike')
async def api_dislike_post(request:Request,dislike_post_info:DLDPostInfo):
    auth_check = check_auth(request)
    post_id = dislike_post_info.post_id

    with sqlconn() as sql:
        def add_dislike():
            like = PostLikes(
            user_id = auth_check["user"],
            post_id = post_id,
            l_d = "Dislike"
        )
            sql.session.add(like)
            sql.session.execute(Update.post_user_dislike_post({"post_id":post_id}))
            sql.session.commit()
        check_l_d_exists = sql.session.execute(Select.postlikes_exists({"user_id":auth_check["user"],"post_id":post_id})).mappings().fetchone()
        if check_l_d_exists:
            if check_l_d_exists["l_d"] == "Like":
                sql.session.execute(Delete.postlikes({"user_id":auth_check["user"],"post_id":post_id,"l_d":"Like"}))
                sql.session.execute(Update.post_user_dislike_post({"post_id":post_id}))
                sql.session.commit()
                add_dislike()
                return MsgResponse(msg="Disliked2")
            elif check_l_d_exists["l_d"] == "Dislike":
                sql.session.execute(Delete.postlikes({"user_id":auth_check["user"],"post_id":post_id,"l_d":"Dislike"}))
                sql.session.execute(Update.post_user_like_post({"post_id":post_id}))
                sql.session.commit()
                return MsgResponse(msg="Undisliked")
        add_dislike()
        return MsgResponse(msg="Disliked")