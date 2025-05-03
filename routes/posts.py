from flask import Blueprint, jsonify, request
from extensions import db
from models import User, Post, Follow
from routes.auth import get_user_id_from_jwt
from routes.user import allowed_file, UPLOAD_FOLDER
from werkzeug.utils import secure_filename
from sqlalchemy.sql import exists
import os
import uuid

post_bp = Blueprint('post_bp', __name__, url_prefix='/post')

@post_bp.route('/upload', methods=['POST'])
def upload_post():
    caption = request.form.get("caption")


    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message' : 'Not authorized'}), 401

    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if 'file' not in request.files:
        return jsonify({'message': 'File not found' }), 404

    file = request.files.get('file')
    if not file:
        return jsonify({'message': 'File not selected' }), 404

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        if not filepath.startswith(UPLOAD_FOLDER):  # ça permet d'éviter les attaques par Directory traversal attack
            return jsonify({"message": "Don't try to hack me ;) "}), 406


        # une fois l'auth vérifiée on assigne la photo uploadée au post de l'utilisateur et ses données qui suivent
        file.save(filepath)
        try:
            new_post = Post(
                image_url=filename,
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
    return jsonify({
        'message' : 'Unsupported Media Type',
    }), 415

@post_bp.route('/<id_post>', methods=['GET'])
def show_post(id_post):
    if not id_post:
        return jsonify({'message': 'Missing the post id'}), 400

    try: 
        uuid_obj = uuid.UUID(id_post)
    except ValueError:
        return jsonify({'message': 'Invalid post ID format please insert only UUID format'}), 400

    post = db.session.query(Post).filter_by(id=id_post).first()
    if not post:
        return jsonify({'message': "The post was not found"}), 404
    user = User.query.get(post.user_id)

    return jsonify({
        'message': 'Post found',
        'post': {
            'id': str(post.id),
            'image_url': post.image_url,
            'caption': post.caption,
            'username': user.username,
            'user_profile_url': user.profile_picture,
            'created_at': str(post.created_at),
        }
    }), 200

@post_bp.route('/feed/global', methods=['GET'])
def global_feed():
    """gestion des posts du feed pour rappel le feed est la page qui rassemble tous les récents posts donc c'est juste un énorme fetch des 10 derniers posts et coté front si la personne scroll au bout du huitieme ça relance un requete"""
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message' : 'Not authorized'}), 401

    posts = db.session.query(Post).order_by(Post.created_at.desc()).limit(10).all() 
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

@post_bp.route('/delete/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message' : 'Not authorized, please log in.'}), 401

    # bug relou: le parametre dans la requete n'est pas un str mais un uuid et donc les caractere comme q, z ne sont pas pris en charge et donc font crash la requete
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

@post_bp.route('/hide/<post_id>', methods=['POST'])
def hide_post(post_id):
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
        return jsonify({'message': 'You are not authorized to edit the visibility of this post'}), 403
    
    if post.hidden_tag is True:
        attribute = False
    else: 
        attribute = True
    try:
        post.hidden_tag = attribute
        db.session.commit()
        return jsonify({
            'message': 'Post passed to hidden successfully',
            'hidden_tag': post.hidden_tag
            }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': f'An error occurred while changing the post attribute: {str(e)}'
            }), 500

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
    new_caption = data.get('caption')
    if not new_caption:
        return jsonify({'message': 'You cannot edit a post without new data...'}), 400
    if len(new_caption) > 200:
        return jsonify({"error": "The caption is too long (max 200 chars)"}), 400

    post.caption = new_caption
    try:
        db.session.commit()
        return jsonify({
            'message': 'Post edited successfully',
            'new_caption': new_caption,
            'last_caption': last_caption
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@post_bp.route('/feed/<user>', methods=['GET'])
def get_user_post(user):
    """Récupérer les posts d'un utilisateur spécifique (ex: profil utilisateur) récupérer tous les posts meme ceux cachés si c'est l'utilisateur concerné (token jwt = user_id) sinon simplement afficher les posts publics de la personne"""
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
        followed_posts = db.session.query(Post).filter(Post.user_id.in_(followed_users)).order_by(Post.created_at.desc()).all()
        return followed_posts