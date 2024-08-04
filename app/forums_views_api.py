
from html import escape
from typing import List, Optional
from fastapi import HTTPException, Request
from pydantic import BaseModel, Field
from sql_dependant.sql_read import Select
from sql_dependant.sql_tables import  Forum
from sql_dependant.sql_connection import sqlconn
from views_api import MsgResponse, check_auth
from main import app
from helpers import listify
from datetime import datetime

class ForumInfo(BaseModel):
    id: int
    page: Optional[int] = 0

class ForumContentsResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

class ForumPostsResponse(BaseModel):
    id : int
    title: str
    link:str
    created_at:datetime
    updated_at:datetime

class ForumPageResponse(BaseModel):
    contents: ForumContentsResponse
    posts: List[ForumPostsResponse]
    postcount:int
    
@app.post('/api/forum',responses={
        200: {
            "description": "Success response",
            "model": ForumPageResponse
        }})
async def api_forum_page(forum_info:ForumInfo):
    id = forum_info.id
    pagenumber = forum_info.page
    with sqlconn() as sql:
        contents = sql.session.execute(Select.forum_page(id)).mappings().fetchone()
        posts = listify(sql.session.execute(Select.posts({"id":id,"page":pagenumber})).mappings().fetchall())
        for post in posts:
            post["link"] = "post?id="+str(post["id"])
        postcount = sql.session.execute(Select.posts_count(id)).mappings().fetchone()
        postcount = (postcount["count"]-1)//10
        return ForumPageResponse(
            contents=ForumContentsResponse(**{k:v for k,v in contents.items()}),
            posts=[ForumPostsResponse(**post) for post in posts],
            postcount=postcount
        )

class ForumsInfo(BaseModel):
    page: Optional[int] = 0


class ForumResponse(BaseModel):
    id : int
    name: str
    description:str
    link:str
    created_at:datetime

class ForumsPageResponse(BaseModel):
    forums: List[ForumResponse]
    page_count:int

@app.post('/api/forums',responses={
        200: {
            "description": "Success response",
            "model": ForumsPageResponse
        }})
async def api_forums_page(forums_info:ForumsInfo):
    pagenumber = forums_info.page
    with sqlconn() as sql:
        forums = listify(sql.session.execute(Select.forums(pagenumber)).mappings().fetchall())
        for forum in forums:
            forum["link"] = "forum?id="+str(forum["id"])
        forumcount = sql.session.execute(Select.forums_count()).mappings().fetchone()
        forumcount = (forumcount["count"]-1)//5
        return ForumsPageResponse(forums=[ForumResponse(**forum) for forum in forums],page_count=forumcount)
    
class ForumCreateInfo(BaseModel):
    name : str = Field(min_length=4)
    description : str = Field(min_length=4)


@app.post('/api/create/forum')
async def api_create_forum(request:Request,forum_create_info:ForumCreateInfo):
    check_auth(request)
    name=escape(forum_create_info.name)
    with sqlconn() as sql:
        forum = Forum(
            name=name,
            description=escape(forum_create_info.description))
        check = sql.session.execute(Select.forum_exists(name)).mappings().fetchall()
        if len(check)>0:
            raise HTTPException(status_code=400, detail="Forum with this name already exists")
        sql.session.add(forum)
        sql.session.commit()
        return MsgResponse(msg="Forum created.")