from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, Integer
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = 'utilisateur'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), unique=True, nullable=False)
    email = Column(String(60), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    bio = Column(String(100), nullable=True)
    website = Column(String(32), nullable=True)
    gender = Column(String(32), nullable=True)
    profile_picture = Column(String(255), nullable=True, default='default.jpg')
    created_at = Column(DateTime, default=utc_now)
    is_admin = Column(Boolean, default=False)

    posts = relationship('Post', backref='author', lazy='joined')

class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_url = Column(String(255), nullable=False)
    caption = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    hidden_tag = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey('utilisateur.id'), nullable=False)
    likes = relationship('Like', backref='post', lazy='joined')
    comments = relationship('Comment', backref='post', lazy='joined')

class Like(Base):
    __tablename__ = 'like'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('utilisateur.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='unique_like'),)

class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    user_id = Column(Integer, ForeignKey('utilisateur.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)

class Follow(Base):
    __tablename__ = 'follow'

    id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id = Column(Integer, ForeignKey('utilisateur.id'), nullable=False)
    followed_id = Column(Integer, ForeignKey('utilisateur.id'), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    __table_args__ = (UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),)

class Notification(Base):
    __tablename__ = 'notification'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('utilisateur.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('utilisateur.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('post.id'), nullable=True)
    type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=utc_now)

class Conversation(Base):
    __tablename__ = 'conversation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user1_id = Column(Integer, ForeignKey('utilisateur.id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('utilisateur.id'), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    messages = relationship('Message', backref='conversation', lazy='joined')

    __table_args__ = (UniqueConstraint('user1_id', 'user2_id', name='unique_conversation'),)

class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey('conversation.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('utilisateur.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now)
    is_read = Column(Boolean, default=False)
