from werkzeug.security import generate_password_hash

# Dans un script ou une commande Flask pour initialiser l'admin
hashed_password = generate_password_hash('admin')
print(hashed_password) 