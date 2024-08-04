from datetime import datetime
from html import escape
from typing import List, Optional
from fastapi import HTTPException, Request
from pydantic import BaseModel, Field
from sql_dependant.sql_read import Select
from sql_dependant.sql_tables import  Post, PostLikes
from sql_dependant.sql_connection import sqlconn
from sql_dependant.sql_write import Update,Delete
from views_api import MsgResponse, check_auth
from main import app
from helpers import listify

class PostInfo(BaseModel):
    id: int
    page: Optional[int] = 0

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
    comments:List[PostCommentsResponse]
    created_by:str
    comment_count:int

@app.post('/api/post',responses={
        200: {
            "description": "Success response",
            "model": PostPageResponse
        }})
async def api_post_page(post_info:PostInfo):
    id = post_info.id
    pagenumber = post_info.page
    with sqlconn() as sql:
        contents = sql.session.execute(Select.post_page(id)).mappings().fetchone()
        if not contents:
            raise HTTPException(status_code=400, detail="This post doesn't exist")
        comments = listify(sql.session.execute(Select.comments({"id":id,"page":pagenumber})).mappings().fetchall())
        comment_count = sql.session.execute(Select.comments_count(id)).mappings().fetchone()
        comment_count = (comment_count["count"]-1)//20
        created_by = sql.session.execute(Select.user_username({"id":contents["user_id"]})).mappings().fetchone()["username"]
        return PostPageResponse(contents = PostContentsResponse(**{k:v for k,v in contents.items()}),
                                comments = [PostCommentsResponse(**comment) for comment in comments],
                                created_by = created_by,comment_count=comment_count
                                )
class CreatePostInfo(BaseModel):
    forum_id : int
    title : str = Field(min_length=4)
    content : str = Field(min_length=4)

@app.post('/api/create/post')
async def api_create_post(request:Request,create_post_info:CreatePostInfo):
    auth_check = check_auth(request)
    forum_id = create_post_info.forum_id
    title=escape(create_post_info.title)
    content=escape(create_post_info.content)
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

@app.post('/api/update/post')
async def api_update_post(request:Request,update_post_info:UpdatePostInfo):
    auth_check = check_auth(request)
    post_id = update_post_info.post_id
    title=escape(update_post_info.title)
    content=escape(update_post_info.content)
    with sqlconn() as sql:
        sql.session.execute(Update.post({"user_id":auth_check["user"],"post_id":post_id,
                                        "title":title,"content":content}))
        sql.session.commit()
    return MsgResponse(msg="Post updated successfully!")

class DLDPostInfo(BaseModel):
    post_id : int

@app.post('/api/delete/post')
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
        like = PostLikes(
            user_id = auth_check["user"],
            post_id = post_id,
            l_d = "Like"
        )
        sql.session.add(like)
        sql.session.execute(Update.post_user_like_post({"post_id":post_id}))
        sql.session.commit()
        return MsgResponse(msg="Liked")

@app.post('/api/post/dislike')
async def api_dislike_post(request:Request,dislike_post_info:DLDPostInfo):
    auth_check = check_auth(request)
    post_id = dislike_post_info.post_id

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
                return MsgResponse(msg="Undisliked")
        like = PostLikes(
            user_id = auth_check["user"],
            post_id = post_id,
            l_d = "Dislike"
        )
        sql.session.add(like)
        sql.session.execute(Update.post_user_dislike_post({"post_id":post_id}))
        sql.session.commit()
        return MsgResponse(msg="Disliked")