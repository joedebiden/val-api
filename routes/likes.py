from flask import Blueprint, jsonify
from models import Post, Like, User
from extensions import db
from routes.auth import get_user_id_from_jwt

like_bp = Blueprint('like', __name__, url_prefix='/like')

@like_bp.route('/<post_id>', methods=['PUT'])
def like_post(post_id):

    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    
    if not Post.query.filter_by(id=post_id).first():
        return jsonify({'message': 'Post not found'}), 404
    
    try:
        new_like = Like(post_id=post_id, user_id=user_id)
        db.session.add(new_like)
        db.session.commit()
        return jsonify({
            'message': 'Post liked successfully',
            'like' : {
                'like_id' : str(new_like.id),
                'post_id' : str(post_id),
                'user_id' : str(user_id),
                'created_at' : str(new_like.created_at)
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500


@like_bp.route('/<post_id>/dislike', methods=['DELETE'])
def dislike_post(post_id):
    
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    
    if not Post.query.filter_by(id=post_id).first():
        return jsonify({'message': 'Post not found'}), 404
    
    like_to_dl = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
    
    if not like_to_dl:
        return jsonify({'message': 'Like not found'}), 404
    try: 
        db.session.delete(like_to_dl)
        db.session.commit()
        return jsonify({
            'message': 'Like removed successfully',
            'like-content':{
                'like_id-removed': str(like_to_dl.id),
                'post_id-attached': str(post_id),
                'user_id-from-like': str(user_id)
            }
            }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500


@like_bp.route('/liked-posts/<user_id>', methods=['GET'])
def get_liked_posts_by_user(user_id):
    current_user = get_user_id_from_jwt()
    if not current_user:
        return jsonify({'message': 'Unauthorized'}), 401
    if not user_id:
        return jsonify({'message': 'User not found'}), 404

    liked_posts_data = (
        db.session.query(Post, Like.created_at)
        .join(Like, Post.id == Like.post_id)
        .join(User, User.id == Like.user_id)
        .filter(Like.user_id == user_id)
        .all()
    )
    posts_list = [
        {
            'post_id': str(post.id),
            'liked_at': str(like_created_at)
        }
        for post, like_created_at in liked_posts_data
    ]
    return jsonify({'liked_posts': posts_list}), 200


@like_bp.route('/get-likes/<post_id>', methods=['GET'])
def get_post_likes(post_id):
    current_user = get_user_id_from_jwt()
    if not current_user:
        return jsonify({'message': 'Unauthorized'}), 401

    if not Post.query.filter_by(id=post_id).first():
        return jsonify({'message': 'Post not found'}), 404

    likes_count = db.session.query(db.func.count(Like.id)).filter(Like.post_id == post_id).scalar()
    
    user_likes = db.session.query(Like.user_id).filter(Like.post_id == post_id).all()
    user_ids = [str(user_id[0]) for user_id in user_likes]

    return jsonify({
        'post_id': str(post_id),
        'likes_count': likes_count,
        'users': user_ids
    }), 200