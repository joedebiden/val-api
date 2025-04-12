from datetime import datetime, timedelta
import uuid
import random
from werkzeug.security import generate_password_hash
from models import User, Post, Follow, db
from app import create_app

def create_test_data():
    app = create_app()
    with app.app_context():
        print("Suppression des données existantes...")
        db.session.query(Follow).delete()
        db.session.query(Post).delete()
        db.session.query(User).delete()
        db.session.commit()

        print("Création des utilisateurs...")
        users = [
            {
                "username": "emma_photo",
                "email": "emma@example.com",
                "password": "password",
                "bio": "Photographe passionnée | Basée à Paris",
                "website": "emmaphotos.com",
                "gender": "Femme",
                "profile_picture": "pic1.jpg",
            },
            {
                "username": "thomas_voyage",
                "email": "thomas@example.com",
                "password": "password",
                "bio": "Voyageur infatigable | 25 pays visités",
                "website": "thomastravel.blog",
                "gender": "Homme",
                "profile_picture": "pic2.jpg",
            },
            {
                "username": "lucie_art",
                "email": "lucie@example.com",
                "password": "password",
                "bio": "Artiste contemporaine | Expositions à Lyon",
                "website": "lucie-art.fr",
                "gender": "Femme",
                "profile_picture": "pic5.jpg"
            },
            {
                "username": "alex_tech",
                "email": "alex@example.com",
                "password": "password",
                "bio": "Développeur full-stack",
                "website": "alexdev.io",
                "gender": "Homme",
                "profile_picture": "pic4.jpg"
            },
            {
                "username": "dev",
                "email": "dev@email.com",
                "password": "dev",
                "bio": "",
                "website": "",
                "gender": "",
                "profile_picture": "pic3.png",
                "is_admin": True
            }
        ]

        # Ajout des utilisateurs
        for user_data in users:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=generate_password_hash(user_data["password"]),
                bio=user_data["bio"],
                website=user_data["website"],
                gender=user_data["gender"],
                profile_picture=user_data["profile_picture"],
            )
            db.session.add(user)
        db.session.commit()

        # Récupération des IDs des utilisateurs depuis la base
        users_from_db = User.query.all()
        user_ids = [user.id for user in users_from_db]

        # Création des posts
        print("Création des posts...")
        posts_data = [
            # Posts pour emma_photo
            {
                "user_index": 0,
                "image_url": "pic9.jpg",
                "caption": "Coucher de soleil sur la Tour Eiffel",
                "days_ago": 5,
            },
            {
                "user_index": 0,
                "image_url": "pic8.jpg",
                "caption": "Shooting en studio aujourd'hui",
                "days_ago": 12,
            },
            # Posts pour thomas_voyage
            {
                "user_index": 1,
                "image_url": "pic7.jpg",
                "caption": "Les plages de Thaïlande",
                "days_ago": 3,
            },
            # Posts pour lucie_art
            {
                "user_index": 2,
                "image_url": "pic6.jpg",
                "caption": "Nouvelle toile terminée",
                "days_ago": 7,
            },
            # Posts pour alex_tech
            {
                "user_index": 3,
                "image_url": "pic5.jpg",
                "caption": "Setup de développement mis à jour",
                "days_ago": 2,
            }
        ]

        for post_data in posts_data:
            user_id = user_ids[post_data["user_index"]]
            post = Post(
                image_url=post_data["image_url"],
                caption=post_data["caption"],
                user_id=user_id,
                hidden_tag=False
            )
            db.session.add(post)

        db.session.commit()
        print(f"- {len(posts_data)} posts créés")

        # Création des relations d'abonnement
        print("Création des abonnements...")
        follows = [
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 0),
            (1, 2),
            (1, 3),
            (2, 0),
            (2, 1),
            (2, 3),
            (3, 0),
            (3, 1),
            (3, 2),
        ]

        for follower_idx, followed_idx in follows:
            follower_id = user_ids[follower_idx]
            followed_id = user_ids[followed_idx]

            follow = Follow(
                follower_id=follower_id,
                followed_id=followed_id,
            )
            db.session.add(follow)

        db.session.commit()
        print(f"- {len(follows)} relations d'abonnement créées")

        print("Jeu de données de test créé avec succès!")


if __name__ == "__main__":
    create_test_data()