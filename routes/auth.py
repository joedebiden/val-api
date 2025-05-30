from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from extensions import db
import jwt 
import datetime
import dotenv
import os
dotenv.load_dotenv()

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')
secret_key = os.environ.get('SECRET_KEY_JWT')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"message": "username or email already exists."}), 400

    try:
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "account created successfully."}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"an error occurred: {str(e)}"}), 500
    
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        user_id = user.id
        user_profile = user.profile_picture if user.profile_picture else None
        token = jwt.encode({
            'id': str(user_id),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }, secret_key, algorithm='HS256')
        return jsonify({
            "token": token,
            "user_id": user_id,
            "username": username,
            "profile_picture": user_profile,
            }), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
    
@auth_bp.route('/token', methods=['POST'])
def token():
    data = request.get_json()
    token = data.get('token')
    user_id = decode_jwt(token)

    if user_id:
        return jsonify({"valid": True}), 200
    else:
        return jsonify({"valid": False}), 401

"""Retourne un user id pour un token JWT en paramètre"""
def get_user_id_from_jwt():
    auth_header = request.headers.get('Authorization')
    if not auth_header or " " not in auth_header:
        return None
    token = auth_header.split()[1]
    data = decode_jwt(token)
    if not data:
        return None
    return data['id']
    
"""Retourne les valeurs décodées du token JWT"""
def decode_jwt(token):
    try:
        return jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

