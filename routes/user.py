from flask import Blueprint, jsonify, request, send_from_directory
from models import User
from extensions import db
from routes.auth import get_user_id_from_jwt, UPLOAD_FOLDER, allowed_file, upload_picture

user_bp = Blueprint('user_bp', __name__, url_prefix='/user')


@user_bp.route('/profile', methods=['GET'])
def profile():
    user_id = get_user_id_from_jwt()
    user = User.query.filter_by(id=user_id).first()
    
    if not user_id:
        return jsonify({"message": "Unauthorized, please log in."}), 401
    
    return jsonify({
        "username": user.username,
        "email": user.email,
        "bio": user.bio,
        "website": user.website,
        "gender": user.gender,
        "profile_picture": user.profile_picture,
        "created_at": user.created_at,  
    }), 200

@user_bp.route('/edit', methods=['POST'])
def edit_profile():
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message' : 'Not authorized, please log in.'}), 401
    
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    new_username = data.get('username')
    new_email = data.get('email')
    new_bio = data.get('bio')
    new_website = data.get('website')
    new_gender = data.get('gender')

    # protection contre l'abus directement vers l'api
    if len(new_username) > 20:
        return jsonify({"error": "Username too long (max 20 chars)"}), 400
    if len(new_bio) > 100:
        return jsonify({"error": "Bio too long (max 50 chars)"}), 400
    if len(new_website) > 32:
        return jsonify({"error": "Website URL too long (max 32 chars)"}), 400
    if len(new_gender) > 32:
        return jsonify({"error": "Gender URL too long (max 32 chars)"}), 400
    

    # si la valeur n'est pas nulle et si elle est différente de celle de base
    # si la requete ne renvoie rien alors ça veut dire que c'est possible de changer
    if new_username and new_username != user.username:
        if User.query.filter_by(username=new_username).first():
            return jsonify({'message' : 'Username already taken'}), 400
        user.username=new_username
    
    if new_email and new_email != user.email:
        if User.query.filter_by(email=new_email).first():
            return jsonify({'message': 'Email already in use'}), 400
        user.email = new_email

    # on accepte ces infos vides mais on ne peut pas la modifier si elle est absente
    if new_bio is not None: 
        user.bio = new_bio

    if new_website is not None:
        user.website = new_website
    
    if new_gender is not None:
        user.gender = new_gender

    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'bio': user.bio,
                'website': user.website,
                'gender': user.gender
            }}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@user_bp.route('/upload-profile-picture', methods=['POST'])
def upload_profile_picture():
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message' : 'Not authorized, please log in.'}), 401
        
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if 'file' not in request.files:
        return jsonify({'message': 'The object File was not found' }), 404
    try:
        picture = upload_picture()
        user.profile_picture = picture
        db.session.commit()
        
        return jsonify({
                'message': 'File uploaded successfully',
                'file_url': f'/user/profile-picture/{picture}'
            }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@user_bp.route('/picture/<filename>', methods=['GET'])
def get_profile_picture(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)

@user_bp.route('/profile/<username>', methods=['GET'])
def profile_user(username):
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message': 'Not authorized, please log in.'}), 401

    user_other = User.query.filter_by(username=username).first()
    if not user_other:  
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'message': 'The user profile info', 
        'username': user_other.username,
        'profile_picture': user_other.profile_picture,
        'bio': user_other.bio,
        'website': user_other.website
    }), 200

@user_bp.route('/search/<username>', methods=['GET'])
def search_people(username):    
    try:
        users = User.query.filter(User.username.ilike(f"%{username}%")).all() # évite toutes erreurs avec la sous chaine 
        if not users:
            return jsonify({'message': 'No user found'}), 404

        result = [{
            'username': user.username,
            'profile_picture': user.profile_picture
        } for user in users]

        return jsonify({
            'message': 'Users found',
            'users': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500