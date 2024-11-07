from html import escape
from typing import Optional,List
from fastapi import HTTPException, Request
from sql_dependant.sql_read import Select
from sql_dependant.sql_tables import Comment, CommentLikes
from sql_dependant.sql_connection import sqlconn
from sql_dependant.sql_write import Delete, Update
from views_api import check_auth,MsgResponse
from main import app
from helpers import limit_line_breaks, listify
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class CreateCommentInfo(BaseModel):
    parent_id: Optional[int] = 0
    post_id: int
    content: str = Field(min_length=4)

@app.post('/api/post/comment')
async def api_create_comment(request:Request,create_comment_info:CreateCommentInfo):
    auth_check = check_auth(request)
    post_id = create_comment_info.post_id
    comment_id = create_comment_info.parent_id
    content = limit_line_breaks(escape(create_comment_info.content),5)
    with sqlconn() as sql:
        comment = Comment(
            user_id = auth_check["user"],
            parent_id = comment_id,
            post_id = post_id,
            content=content)
        sql.session.add(comment)
        sql.session.commit()
        return MsgResponse(msg="Comment created successfully")

class CommentInfo(BaseModel):
    comment_id: int

@app.delete('/api/post/comment')
async def api_delete_comment(request:Request,comment_id: int):
    auth_check = check_auth(request)
    user_id = auth_check["user"]
    comment_id = comment_id
    with sqlconn() as sql:
        check_comment_exists = sql.session.execute(Select.comment(comment_id)).mappings().fetchone()
        if not check_comment_exists:
            raise HTTPException(status_code=400, detail="You can't delete what doesn't exist.")
        
        if not (check_comment_exists["user_id"] == user_id):
            raise HTTPException(status_code=400, detail="You can't delete a comment someone else created.")
        sql.session.execute(Delete.comment({"user_id":user_id,"comment_id":comment_id}))
        sql.session.commit()
        return MsgResponse(msg="Deleted comment")

class RepliesInfo(BaseModel):
    parent_id: int
    post_id: int

class ReplyResponse(BaseModel):
    content: str
    created_at: datetime
    replies: int
    id: int
    likes:int
    parent_id: int
    l_d: str|None
    updated_at: datetime
    username: str


class RepliesResponse(BaseModel):
    replies : List[ReplyResponse]

@app.get('/api/post/{post_id}/comments',responses={
        200: {
            "description": "Success response",
            "model": RepliesResponse
        }})
async def fetch_post_comments(request:Request,post_id:str,parent_id: Optional[int] = 0, page: Optional[int] = 0):
    with sqlconn() as sql:
        data = {"post_id":post_id,"parent_id":parent_id,"page":page}
        try:
            user_info = check_auth(request)
            data["user_id"] = user_info["user"]
        except:
            pass
        replies = sql.session.execute(Select.replies_of_comment(data)).mappings().fetchall()
        return RepliesResponse(replies = replies)

@app.get('/api/post/{post_id}/comment/like')
def api_like_comment(request:Request,post_id:int,comment_id: int):
    auth_check = check_auth(request)
    user_id = auth_check["user"]
    comment_id = comment_id
    with sqlconn() as sql:
        def add_like():
            like = CommentLikes(
            user_id = user_id,
            comment_id = comment_id,
            l_d = "Like"
        )
            sql.session.add(like)
            sql.session.execute(Update.comment_user_like_comment({"comment_id":comment_id}))
            sql.session.commit()
        check_l_d_exists = sql.session.execute(Select.commentlikes_exists({"user_id":user_id,"comment_id":comment_id})).mappings().fetchone()
        if check_l_d_exists:
            if check_l_d_exists["l_d"] == "Like":
                sql.session.execute(Delete.commentlikes({"user_id":user_id,"comment_id":comment_id,"l_d":"Like"}))
                sql.session.execute(Update.comment_user_dislike_comment({"comment_id":comment_id}))
                sql.session.commit()
                return MsgResponse(msg="Unliked")
            elif check_l_d_exists["l_d"] == "Dislike":
                sql.session.execute(Delete.commentlikes({"user_id":user_id,"comment_id":comment_id,"l_d":"Dislike"}))
                sql.session.execute(Update.comment_user_like_comment({"comment_id":comment_id}))
                sql.session.commit()
                add_like()
                return MsgResponse(msg="Liked2")
        add_like()
        return MsgResponse(msg="Liked")

@app.get('/api/post/{post_id}/comment/dislike')
async def api_dislike_comment(request:Request,post_id:int,comment_id: int):
    auth_check = check_auth(request)
    user_id = auth_check["user"]
    comment_id = comment_id

    with sqlconn() as sql:
        def add_dislike():
            like = CommentLikes(
            user_id = user_id,
            comment_id = comment_id,
            l_d = "Dislike"
        )
            sql.session.add(like)
            sql.session.execute(Update.comment_user_dislike_comment({"comment_id":comment_id}))
            sql.session.commit()
        check_l_d_exists = sql.session.execute(Select.commentlikes_exists({"user_id":user_id,"comment_id":comment_id})).mappings().fetchone()
        if check_l_d_exists:
            if check_l_d_exists["l_d"] == "Like":
                sql.session.execute(Delete.commentlikes({"user_id":user_id,"comment_id":comment_id,"l_d":"Like"}))
                sql.session.execute(Update.comment_user_dislike_comment({"comment_id":comment_id}))
                sql.session.commit()
                add_dislike()
                #this tells frontend to deduce 2 likes from the comment since user previously liked it and converted it to dislike
                return MsgResponse(msg="Disliked2")
            elif check_l_d_exists["l_d"] == "Dislike":
                sql.session.execute(Delete.commentlikes({"user_id":user_id,"comment_id":comment_id,"l_d":"Dislike"}))
                sql.session.execute(Update.comment_user_like_comment({"comment_id":comment_id}))
                sql.session.commit()
                return MsgResponse(msg="Undisliked")
        add_dislike()
        return MsgResponse(msg="Disliked")