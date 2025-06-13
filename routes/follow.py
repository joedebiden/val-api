from flask import Blueprint, jsonify, request
from models import User, Follow
from extensions import db
from routes.auth import get_user_id_from_jwt

follow_bp = Blueprint('follows', __name__, url_prefix='/follow')

@follow_bp.route('/user', methods=['POST', 'OPTIONS'])
def follow():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Missing data'}), 404

    username_other = data.get('username_other')
    if not username_other:
        return jsonify({'message': 'Missing username_other field'}), 404

    # Vérifier si username_other est un dictionnaire et extraire le nom d'utilisateur
    if isinstance(username_other, dict) and 'username' in username_other:
        username_other = username_other['username']

    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message': 'Unauthorized, you are not connected or refresh your credentials'}), 401


    user_other = User.query.filter_by(username=username_other).first()
    if not user_other:
        return jsonify({'message': 'User not found'}), 404

    user_id_other = str(user_other.id)

    if user_id == user_id_other:
        return jsonify({'message': "You can't follow yourself"}), 402

    if Follow.query.filter_by(follower_id=user_id, followed_id=user_id_other).first():
        return jsonify({'message': 'Already following'}), 400

    try:
        new_follow = Follow(follower_id=user_id, followed_id=user_id_other)
        db.session.add(new_follow)
        db.session.commit()
        return jsonify({
            'message': 'Followed successfully',
            'follow': {
                'id': str(new_follow.id),
                'follow_id': new_follow.follower_id,
                'followed_id': new_follow.followed_id,
                'created_at': new_follow.created_at
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@follow_bp.route('/unfollow', methods=['POST'])
def unfollow():
    data = request.get_json()

    username_other = data.get('username_other')
    if not data or 'username_other' not in data:
        return jsonify({'message': 'Missing username_other field'}), 404

    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    user_other = User.query.filter_by(username=username_other).first()
    if not user_other:
        return jsonify({'message': 'User not found'}), 404

    user_id_other = str(user_other.id)

    follow_query = Follow.query.filter_by(follower_id=user_id, followed_id=user_id_other).first()

    if follow_query:
        try:
            db.session.delete(follow_query)
            db.session.commit()
            return jsonify({
                'message': 'Unfollow successfully',
                'users': {
                    'ex-follower-id': follow_query.follower_id,
                    'ex-followed-id': follow_query.followed_id,
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'An error occurred: {str(e)}'}), 500
    else:
        return jsonify({'message': 'Follow query not found'}), 404

@follow_bp.route('/get-follow/<username>', methods=['GET'])
def get_user_followers(username):
    user_id = User.query.filter_by(username=username).first().id
    if not user_id:
        return jsonify({'message': 'User not found'}), 404
    try:
        followers = db.session.query(
            User.id,
            User.username,
            User.profile_picture,
            Follow.created_at.label('followed_at')).join(Follow, User.id == Follow.follower_id).filter(
            Follow.followed_id == user_id).order_by(Follow.created_at.desc()).all()

        result = [{
            'id': str(follower.id),
            'username': follower.username,
            'profile_picture': follower.profile_picture,
            'followed_at': follower.followed_at.isoformat()
        } for follower in followers]

        return jsonify({
            'followers': result,
            'count': len(result)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@follow_bp.route('/get-followed/<username>', methods=['GET'])
def get_user_followed(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404
    user_id = user.id
    try:
        followed_users = db.session.query(
            User.id,
            User.username,
            User.profile_picture,
            Follow.created_at.label('followed_at')).join(Follow, User.id == Follow.followed_id).filter(
            Follow.follower_id == user_id).order_by(Follow.created_at.desc()).all()

        result = [{
            'id': str(followed.id),
            'username': followed.username,
            'profile_picture': followed.profile_picture,
            'followed_at': followed.followed_at.isoformat()
        } for followed in followed_users]

        return jsonify({
            'followed': result,
            'count': len(result)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@follow_bp.route('/remove-follower', methods=['DELETE'])
def remove_follower():
    data = request.get_json()

    username_other = data.get('username_other')
    if not data or 'username_other' not in data:
        return jsonify({'message': 'Missing username_other field'}), 404

    user_id = get_user_id_from_jwt()
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    user_other = User.query.filter_by(username=username_other).first()
    if not user_other:
        return jsonify({'message': 'User not found'}), 404

    user_id_other = str(user_other.id)

    follow_query = Follow.query.filter_by(follower_id=user_id_other, followed_id=user_id).first()

    if follow_query:
        try:
            db.session.delete(follow_query)
            db.session.commit()
            return jsonify({
                'message': 'Delete follow relation successfully',
                'users': {
                    'ex-follower-id': follow_query.follower_id,
                    'ex-followed-id': follow_query.followed_id,
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'An error occurred: {str(e)}'}), 500
    else:
        return jsonify({'message': 'Follow query not found'}), 404
