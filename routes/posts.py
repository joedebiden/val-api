from flask import Blueprint, jsonify, request
from extensions import db
from models import User, Post, Follow, Comment, Like
from routes.auth import get_user_id_from_jwt, upload_picture
from sqlalchemy.sql import exists
import uuid

post_bp = Blueprint('post_bp', __name__, url_prefix='/post')

"""
Upload a post with picture and description
"""
@post_bp.route('/upload', methods=['POST'])
def upload_post():
    caption = request.form.get("caption")

    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message' : 'Not authorized'}), 401

    if 'file' not in request.files:
        return jsonify({'message': 'File not found' }), 404

    picture = upload_picture()
    try:
        new_post = Post(
            image_url=picture,
            caption=caption,
            user_id=user_id
        )
        db.session.add(new_post)
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'message': 'An error occurred while updating profile picture'}), 500

    return jsonify({
        'message': 'Post uploaded successfully',
        'post_url': f'/post/{new_post.id}',
        'post': {
            'caption': new_post.caption,
            'user_id':new_post.user_id,
            'created_at': str(new_post.created_at),
        }
    }), 200

"""
Return all the post info with post_id in param
"""
@post_bp.route('/<post_id>', methods=['GET'])
def show_post(post_id):
    if not post_id:
        return jsonify({'message': 'Missing the post id'}), 400
    try: 
        uuid_obj = uuid.UUID(post_id)
    except ValueError:
        return jsonify({'message': 'Invalid post ID format please insert only UUID format'}), 400

    post = db.session.query(Post).filter_by(id=post_id).first()
    if not post:
        return jsonify({'message': "The post was not found"}), 404
    user = User.query.get(post.user_id)
    
    likes_count = db.session.query(db.func.count(Like.id)).filter(Like.post_id == post_id).scalar()
    comments_count = db.session.query(db.func.count(Comment.id)).filter(Comment.post_id == post_id).scalar()

    likes_list = [
        {'like_id': str(like.id)}
        for like in Like.query.filter_by(post_id=post_id).all()
    ]
    comment_list = [
        {'comment_id': str(comment.id)}
        for comment in Comment.query.filter_by(post_id=post_id).all()
    ]
    return jsonify({
        'message': 'Post found',
        'post': {
            'id': str(post.id),
            'image_url': post.image_url,
            'caption': post.caption,
            'username': user.username,
            'user_profile_url': user.profile_picture,
            'created_at': str(post.created_at),
            'hidden_tag': post.hidden_tag,
            'likes' : {
                'likes_count': likes_count,
                'likes_list': likes_list
            },
            'comments': {
                'comments_count': comments_count,
                'comments': comment_list
            }
        }
    }), 200

"""
Feed post management. As a reminder, the feed is the page that gathers
all recent posts, so it's just a huge fetch of the all most recent
posts, and on the frontend if the person scrolls to the eighth one, it triggers another request
"""
@post_bp.route('/feed/global', methods=['GET']) # TODO: Pagination fetch
def global_feed():
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message' : 'Not authorized'}), 401

    # pagination à faire (recuperer tous les posts avec le hidden_tag en false, diviser par 20 (car 20 post par requete) 
    # et a chaque requete active affiche les 20 premiers post puis les 20 prochains autres
    posts = db.session.query(Post).filter_by(hidden_tag=False).order_by(Post.created_at.desc()).all()
    serialized_feed = [
        {
            'id': str(post.id),
            'image_url': post.image_url,
            'caption': post.caption,
            'user_id': post.user_id,
            'username': User.query.get(post.user_id).username,
            'user_profile': User.query.get(post.user_id).profile_picture,
            'created_at': str(post.created_at),
        }
        for post in posts
    ]
    return jsonify({
        'message': 'Feed successfully loaded',
        'content': serialized_feed
    }), 200

"""
Delete a post
"""
@post_bp.route('/delete/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message' : 'Not authorized, please log in.'}), 401

    try: 
        uuid_obj = uuid.UUID(post_id)
    except ValueError:
        return jsonify({'message': 'Invalid post ID format please insert only UUID format'}), 400
    
    post_exists = db.session.query(exists().where(Post.id == post_id)).scalar()
    if not post_exists:
        return jsonify({'message': 'Post not found'}), 404
    
    post = Post.query.filter_by(id=post_id).first()
    if str(post.user_id) != user_id:
        return jsonify({'message': 'You are not authorized to delete this post'}), 403
    
    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Post deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': f'An error occurred while deleting the post: {str(e)}'
            }), 500

"""
Edit a post : caption and tag
"""
@post_bp.route('/edit/<post_id>', methods=['POST'])
def edit_post(post_id):
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message' : 'Not authorized, please log in.'}), 401

    try: 
        uuid_obj = uuid.UUID(post_id)
    except ValueError:
        return jsonify({'message': 'Invalid post ID format please insert only UUID format'}), 400
    
    post_exists = db.session.query(exists().where(Post.id == post_id)).scalar()
    if not post_exists:
        return jsonify({'message': 'Post not found'}), 404
    
    post = Post.query.filter_by(id=post_id).first()
    if str(post.user_id) != user_id:
        return jsonify({'message': 'You are not authorized to edit this post'}), 403
    
    data = request.get_json()
    last_caption = post.caption
    last_tag = post.hidden_tag
    new_caption = data.get('caption')
    new_tag = data.get('hidden_tag')

    if new_caption is not None:
        post.caption = new_caption
    if new_tag is not None:
        post.hidden_tag = new_tag
    
    if post.caption == last_caption and post.hidden_tag == last_tag:
        return jsonify({"message": "No changes detected"}), 204
    
    if len(new_caption) > 200:
        return jsonify({"error": "The caption is too long (max 200 chars)"}), 400

    try:
        db.session.commit()
        return jsonify({
            'message': 'Post edited successfully',
            'new_caption': new_caption,
            'last_caption': last_caption,
            'hidden_tag': post.hidden_tag,
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

"""
Retrieve posts from a specific user (e.g., user profile). 
Get all posts including hidden ones if it's the concerned 
user (token jwt = user_id), otherwise only display the user's public posts.
"""
@post_bp.route('/feed/<user>', methods=['GET'])
def get_user_post(user):
    if not user:
        return jsonify({'message' : 'User not request'}), 401
    target_user = User.query.filter_by(username=user).first().id
    current_user = get_user_id_from_jwt()
    if current_user == str(target_user):
        # show all posts even hidden
        posts = db.session.query(Post).filter(Post.user_id == target_user)
        serialized_posts = [
            {
                'id': post.id,
                'image_url': post.image_url,
                'caption': post.caption,
                'username': User.query.get(post.user_id).username,
                'user_profile': User.query.get(post.user_id).profile_picture,
                'created_at': str(post.created_at),
            }
            for post in posts
        ]
        return jsonify({
            'message': 'Post(s) found',
            'post': serialized_posts
        })
    # else show public post
    posts = db.session.query(Post).filter(Post.user_id == target_user).filter(Post.hidden_tag == False)
    serialized_posts = [
        {
            'id': post.id,
            'image_url': post.image_url,
            'caption': post.caption,
            'username': User.query.get(post.user_id).username,
            'user_profile': User.query.get(post.user_id).profile_picture,
            'created_at': str(post.created_at),
        }
        for post in posts
    ]
    return jsonify({
        'message': 'Post(s) found',
        'post': serialized_posts
    })

"""
Feed of the home page, fetch all content of the followed users of the current user
and do not display the content that are hidden
"""
@post_bp.route('/feed', methods=['GET'])
def feed_perso():
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message' : 'Not authorized'}), 401

    posts = get_followed_posts(user_id)
    serialized_feed = [
        {
            'id': post.id,
            'image_url': post.image_url,
            'caption': post.caption,
            'user_id': post.user_id,
            'username': User.query.get(post.user_id).username,
            'user_profile': User.query.get(post.user_id).profile_picture,
            'created_at': post.created_at,
        }
        for post in posts
    ]
    return jsonify({
        'message': 'Feed successfully loaded',
        'content': serialized_feed
    }), 200

def get_followed_posts(user_id):
        followed_users = db.session.query(Follow.followed_id).filter(Follow.follower_id == user_id).subquery()
        followed_posts = db.session.query(Post).filter(Post.user_id.in_(followed_users)).filter_by(hidden_tag=False).order_by(Post.created_at.desc()).all()
        return followed_posts