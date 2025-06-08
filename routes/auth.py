from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import User
from extensions import db
import jwt 
import datetime
import dotenv
import os
from PIL import Image
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
    
UPLOAD_FOLDER = "public/uploads/"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

"""Methode qui upload une photo, taille réduite, qualité réduite, format jpg, nom sécurisé et retourne le nom de l'image"""
def upload_picture():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            # test du filename avec werkzeug, création d'un suffix date, supp de l'ext, formatage de la date + jpg sur le fichier
            filename = secure_filename(file.filename)
            suffix = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
            name_without_ext = os.path.splitext(filename)[0]
            new_filename = f"{name_without_ext}_{suffix}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, new_filename)

            if not filepath.startswith(UPLOAD_FOLDER):  # prevent Directory traversal attack
                return jsonify({'message': 'Invalid file path, please provide a good filename.' }), 400

            try:
                image = Image.open(file.stream)
                # conversion image en rgb 
                if image.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # reduction de la taille et de la qualité     
                target_size = (1920, 1080)
                image.thumbnail(target_size, Image.Resampling.LANCZOS)
                image.save(filepath, 'JPEG', quality=50, optimize=True)                
                return new_filename

            except Exception as e: 
                return jsonify({'message': f'An error occurred while processing image: {str(e)}'}), 500
        return jsonify({'message': 'Unsupported Media Type'}), 415
    return jsonify({'message': 'Method not allowed'}), 405