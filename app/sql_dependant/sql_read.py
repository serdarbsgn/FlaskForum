import uuid
from sqlalchemy import  delete, func, select, update,desc,not_,exists
from sqlalchemy.orm import aliased
from sqlalchemy.dialects.mysql import insert
from app.sql_dependant.sql_tables import *
from sqlalchemy.sql.functions import coalesce,concat,count

class Select():

    def user_unique_username_email(data):
        statement = select(User.id).where((User.username == data["username"]) | (User.email == data["email"]))
        return statement

    def user_exists_username_password(data):
        statement = select(User.id).where(User.username==data["username"],User.password==data["password"])
        return statement
    
    def user_username(data):
        statement = select(User.username).where(User.id == data["id"])
        return statement
        
    def user_profile_picture(data):
        return select(User.profile_picture).where(User.username == data["user"])
    
    def forums(data):
        statement = select(Forum.id,Forum.name,Forum.description,Forum.created_at).limit(5).offset(data*5)
        return statement
    
    def forums_count():
        return select(count(Forum.id))
    
    def forum_exists(data):
        return select(Forum.id).where(Forum.name == data)
    
    def forum_page(data):
        return select(Forum.id,Forum.name,Forum.description,Forum.created_at).where(Forum.id == data)
    
    def posts(data):
        return select(Post.id,Post.title,Post.created_at,Post.updated_at).where(Post.forum_id == data["id"]).limit(10).offset(data["page"]*10)

    def posts_count(data):
        return select(count(Post.id)).where(Post.forum_id==data)
    
    def post_page(data):
        return select(Post.id,Post.user_id,Post.title,Post.content,Post.created_at,Post.updated_at).where(Post.id == data)
    
    def comments(data):
        CommentAlias = aliased(Comment)
        return select(Comment.id,Comment.parent_id,User.username,Comment.content,Comment.likes,Comment.created_at,Comment.updated_at,exists().where(CommentAlias.parent_id == Comment.id,Comment.post_id == data["id"]
            ).label('has_replies')).join(User,Comment.user_id == User.id).where(
            Comment.post_id == data["id"],Comment.parent_id == 0).limit(20).offset(data["page"]*20).order_by(Comment.id)
    
    def comments_count(data):
        return select(count(Comment.id)).where(Comment.post_id==data,Comment.parent_id == 0)
    
    def replies_of_comment(data):
        CommentAlias = aliased(Comment)
        return select(Comment.id,Comment.parent_id,User.username,Comment.content,Comment.likes,Comment.created_at,Comment.updated_at,exists().where(CommentAlias.parent_id == Comment.id,Comment.post_id == data["post_id"]
           ).label('has_replies')).join(User,Comment.user_id == User.id).where(
           Comment.post_id == data["post_id"],Comment.parent_id == data["parent_id"]).order_by(Comment.id)