import uuid
from sqlalchemy import  delete, func, select, update,desc,not_,exists
from sqlalchemy.orm import aliased
from sqlalchemy.dialects.mysql import insert
from app.sql_dependant.sql_tables import *
from sqlalchemy.sql.functions import coalesce,concat,count

class Select():

    def user_oauth2_email_exists(data):
        return select(User.id,User.email).where(User.email == data["email"])
    def user_post_count(data):
        return select(count(Post.user_id)).where(Post.user_id == data["user_id"])
    def user_karma_point_post(data):
        return select(func.sum(Post.likes)).where(Post.user_id == data["user_id"])
    def user_comment_count(data):
        return select(count(Comment.user_id)).where(Comment.user_id == data["user_id"])
    def user_karma_point_comment(data):
        return select(func.sum(Comment.likes)).where(Comment.user_id == data["user_id"])

    def commentlikes_exists(data):
        return select(CommentLikes.l_d).where(CommentLikes.user_id == data["user_id"],CommentLikes.comment_id == data["comment_id"])
    
    def postlikes_exists(data):
        return select(PostLikes.l_d).where(PostLikes.user_id == data["user_id"],PostLikes.post_id == data["post_id"])
    
    def user_unique_username_email(data):
        statement = select(User.id).where((User.username == data["username"]) | (User.email == data["email"]))
        return statement

    def user_unique_username(data):
        statement = select(User.id).where(User.username == data["username"])
        return statement

    def user_exists_username_password(data):
        statement = select(User.id).where(User.username==data["username"],User.password==data["password"])
        return statement
    
    def user_exists_id_password(data):
        return select(User.username).where(User.id == data["user_id"],User.password == data["password"])

    def user_exists_id_none_password(data):
        return select(User.username).where(User.id == data["user_id"],User.password == None)
    
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
        return select(Post.id,Post.forum_id,Post.user_id,Post.title,Post.content,Post.likes,Post.created_at,Post.updated_at).where(Post.id == data)
    
    def comment(data):
        return select(Comment.id,Comment.parent_id,Comment.user_id,Comment.content,Comment.likes,Comment.created_at,Comment.updated_at).where(Comment.id == data)
    
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
    
    def products():
        statement = select(Product.id,Product.name,Product.description,Product.price,Product.image)
        return statement
    
    def cart(data):
        return select(Cart.id).where(Cart.user_id == data["user"])
    
    def cart_item(data):
        statement = select(CartItem.id,CartItem.cart_id,CartItem.product_id,CartItem.quantity,Product.name,Product.price).join(
        Product, CartItem.product_id == Product.id).where(
        CartItem.cart_id == select(Cart.id).where(Cart.user_id == data["user"]).scalar_subquery())
        return statement
    
    def order_item(data):
        statement = select(OrderItem.id,OrderItem.order_id,OrderItem.product_id,OrderItem.quantity,Product.name,Product.price).join(
        Product, OrderItem.product_id == Product.id).where(
        OrderItem.order_id.in_(select(Order.id).where(Order.user_id == data["user"]).scalar_subquery())).order_by(OrderItem.order_id)
        return statement

    def product_count():
        return select(count(Product.id))    

