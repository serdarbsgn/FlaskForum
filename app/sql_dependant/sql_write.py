import uuid
from sqlalchemy import  delete, func, select, update,desc,not_
from sqlalchemy.dialects.mysql import insert
from app.sql_dependant.sql_tables import *
from sqlalchemy.sql.functions import coalesce,concat,count

class Insert():

    def user(data):
        statement = insert(User)
        return statement

    
class Update():
    
    def user(data):
        statement = update(User).where(User)
        return statement
    
    def user_profile_picture(data):
        statement = update(User).where(User.username == data["id"]).values(profile_picture = data["profile_picture"])
        return statement

class Delete():

    def user(data):
        statement = delete(User).where(User)
        return statement