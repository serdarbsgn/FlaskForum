import uuid
from sqlalchemy import  delete, func, select, update,desc,not_
from sqlalchemy.dialects.mysql import insert
from ..sql_dependant.sql_tables import *
from sqlalchemy.sql.functions import coalesce,concat,count

class Insert():

    def user(data):
        statement = insert(data)
        return statement
    
    def cart_item(data):
        statement = insert(CartItem).values(cart_id=data["cart_id"],product_id=data["product_id"],quantity=data["quantity"]).on_duplicate_key_update(quantity=func.least(CartItem.quantity+data["quantity"],99))
        return statement
 
    
class Update():
    
    def post(data):
        return update(Post).where(Post.id == data["post_id"],Post.user_id  == data["user_id"]).values(title = data["title"],content = data["content"],updated_at = datetime.now())
    
    def user_profile_picture(data):
        statement = update(User).where(User.username == data["id"]).values(profile_picture = data["profile_picture"])
        return statement
    
    def user_username(data):
        return update(User).where(User.id == data["id"]).values(username = data["username"])
    
    def user_password(data):
        return update(User).where(User.id == data["user_id"]).values(password = data["password"])
    
    def comment_user_like_comment(data):
        return update(Comment).where(Comment.id == data["comment_id"]).values(likes = Comment.likes + 1)
    
    def comment_user_dislike_comment(data):
        return update(Comment).where(Comment.id == data["comment_id"]).values(likes = Comment.likes - 1)
    
    def post_user_like_post(data):
        return update(Post).where(Post.id == data["post_id"]).values(likes = Post.likes + 1)
    
    def post_user_dislike_post(data):
        return update(Post).where(Post.id == data["post_id"]).values(likes = Post.likes - 1)
   
    def cart_item(data):
        statement = update(CartItem).where(CartItem.cart_id==data["cart_id"],CartItem.product_id==data["product_id"]).values(quantity = data["quantity"])
        return statement

class Delete():
    def user(data):
        return delete(User).where(User.id == data["id"],User.username == data["username"])
    def comment(data):
        return delete(Comment).where(Comment.id == data["comment_id"],Comment.user_id == data["user_id"])
    def post(data):
        return delete(Post).where(Post.id == data["post_id"],Post.user_id == data["user_id"])
    def commentlikes(data):
        return delete(CommentLikes).where(CommentLikes.user_id == data["user_id"],CommentLikes.comment_id==data["comment_id"],CommentLikes.l_d==data["l_d"])
    def postlikes(data):
        return delete(PostLikes).where(PostLikes.user_id == data["user_id"],PostLikes.post_id == data["post_id"],PostLikes.l_d==data["l_d"])
    def cart_item(data):
        statement = delete(CartItem).where(CartItem.cart_id==data["cart_id"],CartItem.product_id==data["product_id"])
        return statement
    def cart(data):
        statement = delete(Cart).where(Cart.user_id == data["user"])
        return statement