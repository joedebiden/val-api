from datetime import datetime
import uuid
from extensions import db

""" 
Table User
"""
class User(db.Model):
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(32), nullable=True)
    gender = db.Column(db.String(32), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True, default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy=True)



""" 
Table Post
Publications
"""
class Post(db.Model):
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    hidden_tag = db.Column(db.Boolean, default=False) # tag qui permet de définir si le post doit être caché ou non 

    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('Like', backref='post', lazy=True)
    comments = db.relationship('Comment', backref='post', lazy=True)


"""
Table Like
m'entions j'aime
"""
class Like(db.Model):
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_arg__ = (db.UniqueConstraint(user_id, post_id, name='unique_like'),) # Un seul utilisateur unique par like de post


"""
Table Comment
commentaires d'un post
"""
class Comment(db.Model):
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('post.id'), nullable=False)


"""
Table Follow
les abonnements
"""
class Follow(db.Model):
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_arg__ = (db.UniqueConstraint(follower_id, followed_id, name='unique_follow'),) # Une seule relation entre deux utilisateurs



"""
Table Notification
les notifs(likes, comments, follows)
"""
class Notification(db.Model):
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)  # À qui appartient la notif
    sender_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)  # Qui a généré la notif
    post_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('post.id'), nullable=True)  # Optionnel (si lié à un post)
    type = db.Column(db.String(50), nullable=False)  # Ex: "like", "comment", "follow"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


"""
Table conversation
discussions entre utilisateurs (entre deux personnes)
Groups implementation to see later
"""
class Conversation(db.Model):
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user1_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)  # Premier utilisateur
    user2_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)  # Deuxième utilisateur
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship('Message', backref='conversation', lazy=True)

    __table_arg__ = (db.UniqueConstraint(user1_id, user2_id, name='unique_conversation'),)  # Une seule conv entre deux users


"""
Table Message
messages envoyés à l'utilisateur
"""
class Message(db.Model):
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('conversation.id'), nullable=False)
    sender_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)