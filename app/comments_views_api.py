from html import escape
from typing import Optional,List
from fastapi import HTTPException, Request
from sql_dependant.sql_read import Select
from sql_dependant.sql_tables import Comment, CommentLikes
from sql_dependant.sql_connection import sqlconn
from sql_dependant.sql_write import Delete, Update
from views_api import check_auth,MsgResponse
from main import app
from helpers import listify
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class CreateCommentInfo(BaseModel):
    parent_id: Optional[int] = 0
    post_id: int
    content: str = Field(min_length=4)

@app.post('/api/create/comment')
async def api_create_comment(request:Request,create_comment_info:CreateCommentInfo):
    auth_check = check_auth(request)
    post_id = create_comment_info.post_id
    comment_id = create_comment_info.parent_id

    with sqlconn() as sql:
        comment = Comment(
            user_id = auth_check["user"],
            parent_id = comment_id,
            post_id = post_id,
            content=escape(create_comment_info.content))
        sql.session.add(comment)
        sql.session.commit()
        return MsgResponse(msg="Comment created successfully")

class CommentInfo(BaseModel):
    comment_id: int

@app.post('/api/delete/comment')
async def api_delete_comment(request:Request,delete_comment_info:CommentInfo):
    auth_check = check_auth(request)
    comment_id = delete_comment_info.comment_id

    with sqlconn() as sql:
        check_comment_exists = sql.session.execute(Select.comment(comment_id)).mappings().fetchone()
        if not check_comment_exists:
            raise HTTPException(status_code=400, detail="You can't delete what doesn't exist.")
        
        if not (check_comment_exists["user_id"] == auth_check["user_id"]):
            raise HTTPException(status_code=400, detail="You can't delete a comment someone else created.")
        sql.session.execute(Delete.comment({"user_id":auth_check["user_id"],"comment_id":comment_id}))
        sql.session.commit()
        return MsgResponse(msg="Deleted comment")

class RepliesInfo(BaseModel):
    parent_id: int
    post_id: int

class ReplyResponse(BaseModel):
    content: str
    created_at: datetime
    has_replies: bool
    id: int
    likes:int
    parent_id:int
    updated_at: datetime
    username:str

class RepliesResponse(BaseModel):
    replies : List[ReplyResponse]

@app.post('/api/fetch/replies')
async def api_fetch_replies(replies_info:RepliesInfo):
    with sqlconn() as sql:
        replies = listify(sql.session.execute(Select.replies_of_comment({"post_id":replies_info.post_id,"parent_id":replies_info.parent_id})).mappings().fetchall())
        return RepliesResponse(replies = [ReplyResponse(**reply) for reply in replies])


@app.post('/api/comment/like')
def api_like_comment(request:Request,like_comment_info:CommentInfo):
    auth_check = check_auth(request)
    user_id = auth_check["user"]
    comment_id = like_comment_info.comment_id

    with sqlconn() as sql:
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
        like = CommentLikes(
            user_id = escape(user_id),
            comment_id = escape(comment_id),
            l_d = "Like"
        )
        sql.session.add(like)
        sql.session.execute(Update.comment_user_like_comment({"comment_id":comment_id}))
        sql.session.commit()
        return MsgResponse(msg="Liked")

@app.post('/api/comment/dislike')
async def api_dislike_comment(request:Request,dislike_comment_info:CommentInfo):
    auth_check = check_auth(request)
    user_id = auth_check["user"]
    comment_id = dislike_comment_info.comment_id

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
                return MsgResponse(msg="Undisliked")
        like = CommentLikes(
            user_id = escape(user_id),
            comment_id = escape(comment_id),
            l_d = "Dislike"
        )
        sql.session.add(like)
        sql.session.execute(Update.comment_user_dislike_comment({"comment_id":comment_id}))
        sql.session.commit()
        return MsgResponse(msg="Disliked")