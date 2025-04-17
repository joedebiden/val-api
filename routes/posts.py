from flask import Blueprint, jsonify, request
from extensions import db
from models import User, Post, Follow
from routes.auth import get_user_id_from_jwt
from routes.user import allowed_file, UPLOAD_FOLDER
from werkzeug.utils import secure_filename
import os

post_bp = Blueprint('post_bp', __name__, url_prefix='/post')


"""
Upload un nouveau post
- image_url => upload photo 
- caption 
- hidden_tag => false/true
- user_id 
"""
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


"""
route pour afficher les infos d'un post
/!\ à faire - renvoyer les commentaires et likes associés au post
"""
@post_bp.route('/<id_post>', methods=['GET'])
def show_post(id_post):
    if not id_post:
        return jsonify({'message': 'Missing the post id'}), 400

    #post = Post.query.filter_by(id=id_post).first()
    post = db.session.query(Post).filter_by(id=id_post).first()

    user = User.query.get(post.user_id)
    if not post:
        return jsonify({'message': "The post was not found"}), 404

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

""" gestion des posts du feed 
1. Récupérer la liste des utilisateurs suivis par l'utilisateur connecté.
2. Récupérer leurs posts, triés par date (du plus récent au plus ancien).
3. Récupérer une liste d'autres utilisateurs (exclure ceux suivis).
4. Récupérer aléatoirement des posts parmi ces utilisateurs
5. Fusionner les deux listes (posts des abonnés en premier et par date décroissante)
"""
@post_bp.route('/feed', methods=['GET'])
def feed_post():
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message' : 'Not authorized'}), 401

    feed = get_feed(user_id) # array
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
        for post in feed
    ]
    return jsonify({
        'message': 'Feed successfully loaded',
        'content': serialized_feed
    }), 200

def get_followed_posts(user_id):
    # récupération des utilisateurs suivis
    followed_users = db.session.query(Follow.followed_id).filter(Follow.followed_id==user_id).subquery()
    # récup des 2 derniers posts des abonnements
    followed_posts = db.session.query(Post).filter(Post.user_id.in_(followed_users)).order_by(Post.created_at.desc()).limit(2).all()
    return followed_posts

def get_random_posts(user_id):
    followed_users = db.session.query(Follow.followed_id).filter(Follow.follower_id == user_id).subquery()
    # récup 10 personnes aléatoires en excluant ceux qui sont suivis 
    random_users = db.session.query(User.id).filter(~User.id.in_(followed_users)).order_by(db.func.random()).limit(10).subquery()
    # retourne 1 post le plus récent par personne
    random_post = db.session.query(Post).filter(Post.user_id.in_(random_users)).order_by(db.func.random()).first()
    return random_post

"""merging des fonctions followed_posts & random_post sous forme d'array"""
def get_feed(user_id):
    posts = get_followed_posts(user_id)
    random_post = get_random_posts(user_id)
    if random_post:
        posts.append(random_post)
    return posts



@post_bp.route('/delete', methods=['POST'])
def delete_post():
    return

# Récupérer tous les posts (ex: page Explore).
@post_bp.route('/get-all', methods=['POST'])
def get_all_post():
    return

# Récupérer les posts d'un utilisateur spécifique (ex: profil utilisateur).
# récupérer tous les posts meme ceux cachés si c'est l'utilisateur concerné (token jwt = user_id)
# sinon simplement afficher les posts publics de la personne
@post_bp.route('/get-user/<user>', methods=['POST'])
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

# Récupérer les posts des personnes suivies (ex: feed principal).
@post_bp.route('/get-followed', methods=['POST'])
def get_followed_post():
    return