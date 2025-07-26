from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = 'utilisateur'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(20), unique=True, nullable=False)
    email = Column(String(60), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)
    website = Column(String(32), nullable=True)
    gender = Column(String(32), nullable=True)
    profile_picture = Column(String(255), nullable=True, default='default.jpg')
    created_at = Column(DateTime, default=utc_now)
    is_admin = Column(Boolean, default=False)

    posts = relationship('Post', backref='author', lazy='joined')

class Post(Base):
    __tablename__ = 'post'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_url = Column(String(255), nullable=False)
    caption = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    hidden_tag = Column(Boolean, default=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)
    likes = relationship('Like', backref='post', lazy='joined')
    comments = relationship('Comment', backref='post', lazy='joined')

class Like(Base):
    __tablename__ = 'like'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey('post.id'), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='unique_like'),)

class Comment(Base):
    __tablename__ = 'comment'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    user_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey('post.id'), nullable=False)

class Follow(Base):
    __tablename__ = 'follow'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)
    followed_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    __table_args__ = (UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),)

class Notification(Base):
    __tablename__ = 'notification'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey('post.id'), nullable=True)
    type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=utc_now)

class Conversation(Base):
    __tablename__ = 'conversation'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user1_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)
    user2_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    messages = relationship('Message', backref='conversation', lazy='joined')

    __table_args__ = (UniqueConstraint('user1_id', 'user2_id', name='unique_conversation'),)

class Message(Base):
    __tablename__ = 'message'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey('conversation.id'), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey('utilisateur.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)
    is_read = Column(Boolean, default=False)
