from flask import Blueprint, jsonify, request, send_from_directory
from models import User, Follow
from extensions import db
from routes.auth import get_user_id_from_jwt
from werkzeug.utils import secure_filename
import os 

user_bp = Blueprint('user_bp', __name__, url_prefix='/user')



""" 
Profil 
L'utilisateur est connecté et clique sur 'Profil'.
React envoie une requête POST /user/profile.
Objectif est de récupérer le username, email, photo de profil, bio, date de création à partir du token JWT 
"""
@user_bp.route('/profile', methods=['POST'])
def profile():
    user_id = get_user_id_from_jwt()
    user = User.query.filter_by(id=user_id).first()
    
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    return jsonify({
        "username": user.username,
        "email": user.email,
        "bio": user.bio,
        "website": user.website,
        "gender": user.gender,
        "profile_picture": user.profile_picture,
        "created_at": user.created_at,  
    }), 200


"""
Modification du profil utilisateur
"""
@user_bp.route('/edit', methods=['POST'])
def edit_profile():
    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message' : 'Not authorized'}), 401
    
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
    if len(new_bio) > 50:
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



UPLOAD_FOLDER = "public/uploads/"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


"""
Route pour upload une photo de profil.

Cette route accepte uniquement les requêtes POST. Elle vérifie d'abord si un fichier a été envoyé
dans la requête. Si aucun fichier n'est trouvé, elle retourne un message d'erreur avec le code 404.
Ensuite, elle vérifie si le fichier est valide et s'il est autorisé (en utilisant la fonction allowed_file).
Si le fichier est valide, il est sauvegardé dans le dossier UPLOAD_FOLDER après avoir sécurisé son nom
de fichier avec secure_filename. Une protection contre les attaques de type path traversal est également
mise en place pour s'assurer que le chemin du fichier est valide. Si tout se passe bien, un message de
succès est retourné avec l'URL du fichier uploadé.

De plus la route doit assigner l'image à la personne, donc elle prend le nom du fichier et le modifie pour avoir un id unique
ensuite on modifie le profile_picture de l'utilisateur pour mettre le meme que celui du fichier uploadé. 
Returns:
    Response: Un objet JSON contenant un message et, en cas de succès, l'URL du fichier uploadé.
"""
@user_bp.route('/upload-profile-picture', methods=['POST'])
def upload_profile_picture():
    if request.method == 'POST':
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

            if not filepath.startswith(UPLOAD_FOLDER):  # ça permet d'éviter les attaques par chemin truc bidule
                return jsonify({'message': 'Invalid file path' }), 400
            

            # une fois l'auth vérifiée on assigne la photo uploadée a l'utilisateur et on update son profil
            file.save(filepath)
            try:
                user.profile_picture = filename
                db.session.commit()
            except: 
                db.session.rollback()
                return jsonify({'message': 'An error occurred while updating profile picture'}), 500
            
            return jsonify({
                'message': 'File uploaded successfully',
                'file_url': f'/user/profile-picture/{filename}'
            }), 200
        return jsonify({
            'message': 'Unsupported Media Type',
        }), 415
    return jsonify({
        'message': 'Method not allowed',
    }), 405


"""
Récupération des photos de profil dans le path
"""
@user_bp.route('/profile-picture/<filename>', methods=['GET'])
def get_profile_picture(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)



"""affiche le profil d'une personne
! il faut etre connecté pour voir le profil d'un utilisateur
retourne un json contenant les informations: 
- username
- profile_picture
- date_creation
- bio
- site web
"""
@user_bp.route('/profile/<username>', methods=['GET', 'POST'])
def profile_user(username):
    user_id = get_user_id_from_jwt() # il faut etre connecté pour afficher le profil d'une personne
    if not user_id:
        return jsonify({'message': 'Need to be connected - Unauthorized'}), 401

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

    

"""
Cette route permet de rechercher des utilisateurs par leur nom d'utilisateur. Elle effectue une recherche
insensible à la casse en utilisant le nom d'utilisateur fourni comme sous-chaîne. Si des utilisateurs correspondants
sont trouvés, leurs noms d'utilisateur et photos de profil sont retournés dans la réponse.
Paramètres de la requête :
- username (str) : Le nom d'utilisateur ou une partie du nom d'utilisateur à rechercher.
Réponses :
- 200 OK : Retourne un objet JSON contenant une liste d'utilisateurs avec leurs noms d'utilisateur et photos de profil.
- 404 Not Found : Retourne un objet JSON avec un message indiquant qu'aucun utilisateur n'a été trouvé.
- 500 Internal Server Error : Retourne un objet JSON avec un message d'erreur en cas d'exception.
"""
@user_bp.route('/search/<username>', methods=['GET'])
def search_people(username):
    try:
        users = User.query.filter(User.username.ilike(f"%{username}%")).all() # évite toutes erreurs avec la sous chaine 
        if not users:
            return jsonify({'message': 'No users found'}), 404

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