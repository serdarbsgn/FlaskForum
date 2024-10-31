
from html import escape
from typing import List, Optional
from fastapi import HTTPException, Query, Request
from pydantic import BaseModel, Field
from sql_dependant.sql_read import Select
from sql_dependant.sql_tables import  Forum
from sql_dependant.sql_connection import sqlconn
from views_api import MsgResponse, check_auth
from main import app
from helpers import limit_line_breaks, listify
from datetime import datetime

class ForumContentsResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

class ForumPostsResponse(BaseModel):
    id : int
    title: str
    created_at:datetime
    updated_at:datetime

class ForumPageResponse(BaseModel):
    contents: ForumContentsResponse
    posts: List[ForumPostsResponse]
    postcount:int
    
@app.get('/api/forum/{forum_id}',responses={
        200: {
            "description": "Success response",
            "model": ForumPageResponse
        }})
async def api_forum_page(forum_id:int ,page: int = Query(0, description="Page number for pagination") ):
    id = forum_id
    pagenumber = page
    with sqlconn() as sql:
        contents = sql.session.execute(Select.forum_page(id)).mappings().fetchone()
        posts = listify(sql.session.execute(Select.posts({"id":id,"page":pagenumber})).mappings().fetchall())
        postcount = sql.session.execute(Select.posts_count(id)).mappings().fetchone()
        postcount = (postcount["count"]-1)//10
        return ForumPageResponse(
            contents=contents,
            posts=posts,
            postcount=postcount
        )

class ForumResponse(BaseModel):
    id : int
    name: str
    description:str
    created_at:datetime

class ForumsPageResponse(BaseModel):
    forums: List[ForumResponse]
    page_count:int

@app.get('/api/forums',responses={
        200: {
            "description": "Success response",
            "model": ForumsPageResponse
        }})
async def api_forums_page(page: int = Query(0, description="Page number for pagination")):
    pagenumber = page
    with sqlconn() as sql:
        forums = listify(sql.session.execute(Select.forums(pagenumber)).mappings().fetchall())
        forumcount = sql.session.execute(Select.forums_count()).mappings().fetchone()
        forumcount = (forumcount["count"]-1)//5
        return ForumsPageResponse(forums=forums,page_count=forumcount)
    
class ForumCreateInfo(BaseModel):
    name : str = Field(min_length=4)
    description : str = Field(min_length=4)


@app.post('/api/forum')
async def api_create_forum(request:Request,forum_create_info:ForumCreateInfo):
    check_auth(request)
    name=escape(forum_create_info.name)
    with sqlconn() as sql:
        forum = Forum(
            name=name,
            description=limit_line_breaks(escape(forum_create_info.description),31))
        check = sql.session.execute(Select.forum_exists(name)).mappings().fetchall()
        if len(check)>0:
            raise HTTPException(status_code=400, detail="Forum with this name already exists")
        sql.session.add(forum)
        sql.session.commit()
        return MsgResponse(msg="Forum created.")