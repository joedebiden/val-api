from datetime import datetime, timedelta
import uuid
import random
from werkzeug.security import generate_password_hash
from models import User, Post, Follow, Conversation, db


def create_test_data():
    # Vider les tables existantes
    db.session.query(Follow).delete()
    db.session.query(Post).delete()
    db.session.query(User).delete()
    db.session.commit()

    # Création des utilisateurs
    users = [
        {
            "username": "emma_photo",
            "email": "emma@example.com",
            "password": "Password123!",
            "bio": "Photographe passionnée | Basée à Paris | Découvrez mon univers visuel",
            "website": "emmaphotos.com",
            "gender": "Femme",
            "profile_picture": "emma.jpg"
        },
        {
            "username": "thomas_voyage",
            "email": "thomas@example.com",
            "password": "Password123!",
            "bio": "Voyageur infatigable | 25 pays visités | Conseils de voyage",
            "website": "thomastravel.blog",
            "gender": "Homme",
            "profile_picture": "thomas.jpg"
        },
        {
            "username": "lucie_art",
            "email": "lucie@example.com",
            "password": "Password123!",
            "bio": "Artiste contemporaine | Expositions à Lyon | Amoureuse des couleurs",
            "website": "lucie-art.fr",
            "gender": "Femme",
            "profile_picture": "lucie.jpg"
        },
        {
            "username": "alex_tech",
            "email": "alex@example.com",
            "password": "Password123!",
            "bio": "Développeur full-stack | Passionné de nouvelles technologies | Mentor",
            "website": "alexdev.io",
            "gender": "Homme",
            "profile_picture": "alex.jpg"
        },
        {
            "username": "sophie_cuisine",
            "email": "sophie@example.com",
            "password": "Password123!",
            "bio": "Chef à domicile | Recettes créatives | Blogueuse culinaire",
            "website": "sophie-cuisine.com",
            "gender": "Femme",
            "profile_picture": "sophie.jpg"
        },
        {
            "username": "maxime_sport",
            "email": "maxime@example.com",
            "password": "Password123!",
            "bio": "Coach sportif | Triathlon | Nutrition | Préparation physique",
            "website": "maximecoach.fr",
            "gender": "Homme",
            "profile_picture": "maxime.jpg"
        },
        {
            "username": "chloe_mode",
            "email": "chloe@example.com",
            "password": "Password123!",
            "bio": "Styliste | Tendances mode | Conseils personnalisés",
            "website": "chloe-style.com",
            "gender": "Femme",
            "profile_picture": "chloe.jpg"
        }
    ]

    # Ajout des utilisateurs
    user_objects = []
    for user_data in users:
        user = User(
            id=uuid.uuid4(),
            username=user_data["username"],
            email=user_data["email"],
            password_hash=generate_password_hash(user_data["password"]),
            bio=user_data["bio"],
            website=user_data["website"],
            gender=user_data["gender"],
            profile_picture=user_data["profile_picture"],
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
        )
        db.session.add(user)
        user_objects.append(user)

    db.session.commit()

    # Création des posts
    posts_data = [
        # Posts pour emma_photo
        {
            "user_index": 0,
            "image_url": "emma_post1.jpg",
            "caption": "Coucher de soleil sur la Tour Eiffel. La magie parisienne à son apogée! #Paris #Photography",
            "days_ago": 5,
        },
        {
            "user_index": 0,
            "image_url": "emma_post2.jpg",
            "caption": "Shooting en studio aujourd'hui. J'adore travailler avec l'éclairage artificiel. #PortraitPhotography",
            "days_ago": 12,
        },
        {
            "user_index": 0,
            "image_url": "emma_post3.jpg",
            "caption": "Architecture contemporaine - lignes et perspectives #Architecture #UrbanPhotography",
            "days_ago": 20,
        },

        # Posts pour thomas_voyage
        {
            "user_index": 1,
            "image_url": "thomas_post1.jpg",
            "caption": "Les plages de Thaïlande sont toujours aussi magiques. Premier jour à Koh Phi Phi! #Thailand #Travel",
            "days_ago": 3,
        },
        {
            "user_index": 1,
            "image_url": "thomas_post2.jpg",
            "caption": "Trek dans les montagnes du Népal - jour 4. La vue en vaut chaque pas! #Nepal #Trekking #Himalayas",
            "days_ago": 15,
        },

        # Posts pour lucie_art
        {
            "user_index": 2,
            "image_url": "lucie_post1.jpg",
            "caption": "Nouvelle toile terminée! 'Émotions abstraites' - acrylique sur toile, 80x100cm #ContemporaryArt",
            "days_ago": 7,
        },
        {
            "user_index": 2,
            "image_url": "lucie_post2.jpg",
            "caption": "Préparation de ma prochaine exposition à la galerie Artème. Vernissage le 15 mai! #Exhibition",
            "days_ago": 10,
        },
        {
            "user_index": 2,
            "image_url": "lucie_post3.jpg",
            "caption": "Expérimentation avec de nouvelles techniques mixtes #MixedMedia #ArtProcess",
            "days_ago": 18,
        },

        # Posts pour alex_tech
        {
            "user_index": 3,
            "image_url": "alex_post1.jpg",
            "caption": "Setup de développement mis à jour! Prêt pour de nouveaux projets #DeveloperLife #Coding",
            "days_ago": 2,
        },
        {
            "user_index": 3,
            "image_url": "alex_post2.jpg",
            "caption": "Au hackathon de Lyon ce weekend. Notre équipe travaille sur une app de gestion environnementale #Hackathon",
            "days_ago": 14,
        },

        # Posts pour sophie_cuisine
        {
            "user_index": 4,
            "image_url": "sophie_post1.jpg",
            "caption": "Tarte aux fraises revisitée avec crème pâtissière au basilic #Dessert #Patisserie",
            "days_ago": 4,
        },
        {
            "user_index": 4,
            "image_url": "sophie_post2.jpg",
            "caption": "Atelier cuisine 'saveurs d'Asie' aujourd'hui. Tout le monde a adoré les raviolis à la vapeur! #CookingClass",
            "days_ago": 9,
        },
        {
            "user_index": 4,
            "image_url": "sophie_post3.jpg",
            "caption": "Visite du marché ce matin. Inspiration pour le menu de la semaine! #FreshIngredients #FoodLover",
            "days_ago": 16,
        },

        # Posts pour maxime_sport
        {
            "user_index": 5,
            "image_url": "maxime_post1.jpg",
            "caption": "Triathlon de Nice terminé! 1.5km natation, 40km vélo, 10km course. Épuisé mais heureux! #Triathlon",
            "days_ago": 6,
        },
        {
            "user_index": 5,
            "image_url": "maxime_post2.jpg",
            "caption": "Session d'entraînement de haute intensité avec mes clients aujourd'hui #HIIT #PersonalTrainer",
            "days_ago": 11,
        },

        # Posts pour chloe_mode
        {
            "user_index": 6,
            "image_url": "chloe_post1.jpg",
            "caption": "Tendances printemps-été: couleurs vives et imprimés floraux #FashionTrends #Style",
            "days_ago": 8,
        },
        {
            "user_index": 6,
            "image_url": "chloe_post2.jpg",
            "caption": "Shooting pour ma nouvelle collection capsule. Merci à @emma_photo pour les superbes photos! #NewCollection",
            "days_ago": 13,
        },
        {
            "user_index": 6,
            "image_url": "chloe_post3.jpg",
            "caption": "Conseils styling: comment accessoiriser une tenue minimaliste #StylingTips #FashionAdvice",
            "days_ago": 19,
        }
    ]

    for post_data in posts_data:
        user = user_objects[post_data["user_index"]]
        post = Post(
            id=uuid.uuid4(),
            image_url=post_data["image_url"],
            caption=post_data["caption"],
            created_at=datetime.utcnow() - timedelta(days=post_data["days_ago"]),
            user_id=user.id,
            hidden_tag=False
        )
        db.session.add(post)

    db.session.commit()

    # Création des relations d'abonnement
    # Définition de qui suit qui
    follows = [
        # Emma suit
        (0, 1),  # Emma suit Thomas
        (0, 2),  # Emma suit Lucie
        (0, 6),  # Emma suit Chloé

        # Thomas suit
        (1, 0),  # Thomas suit Emma
        (1, 4),  # Thomas suit Sophie
        (1, 5),  # Thomas suit Maxime

        # Lucie suit
        (2, 0),  # Lucie suit Emma
        (2, 6),  # Lucie suit Chloé

        # Alex suit
        (3, 0),  # Alex suit Emma
        (3, 1),  # Alex suit Thomas
        (3, 5),  # Alex suit Maxime

        # Sophie suit
        (4, 0),  # Sophie suit Emma
        (4, 2),  # Sophie suit Lucie
        (4, 6),  # Sophie suit Chloé

        # Maxime suit
        (5, 1),  # Maxime suit Thomas
        (5, 3),  # Maxime suit Alex
        (5, 4),  # Maxime suit Sophie

        # Chloé suit
        (6, 0),  # Chloé suit Emma
        (6, 2),  # Chloé suit Lucie
        (6, 4),  # Chloé suit Sophie
    ]

    for follower_idx, followed_idx in follows:
        follower = user_objects[follower_idx]
        followed = user_objects[followed_idx]

        # Création de quelques jours dans le passé
        days_ago = random.randint(1, 30)

        follow = Follow(
            id=uuid.uuid4(),
            follower_id=follower.id,
            followed_id=followed.id,
            created_at=datetime.utcnow() - timedelta(days=days_ago)
        )
        db.session.add(follow)

    db.session.commit()

    print("Jeu de données de test créé avec succès!")
    print(f"- {len(users)} utilisateurs")
    print(f"- {len(posts_data)} posts")
    print(f"- {len(follows)} relations d'abonnement")


if __name__ == "__main__":
    create_test_data()