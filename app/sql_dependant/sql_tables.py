from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, Text, DECIMAL,ForeignKey,String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(25), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    profile_picture = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class Forum(Base):
    __tablename__ = 'forums'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    forum_id = Column(Integer, ForeignKey('forums.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    likes = Column(Integer,default = 0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer,default=0,nullable=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text)
    likes = Column(Integer,default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class CommentLikes(Base):
    __tablename__ = "comment_likes"
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, primary_key=True)
    comment_id = Column(Integer, ForeignKey('comments.id'), nullable=False, primary_key=True)
    l_d = Column(String(7),default = "Like")

class PostLikes(Base):
    __tablename__ = "post_likes"
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False, primary_key=True)
    l_d = Column(String(7),default = "Like")