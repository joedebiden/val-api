import jwt
from fastapi import UploadFile, Request, HTTPException
from PIL import Image
import os
from datetime import datetime
from uuid import uuid4

from app.core.config import settings


UPLOAD_FOLDER = "public/uploads/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def decode_jwt(token: str):
    """Returns the decoded values of the JWT token"""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def jwt_user_id(request: Request) -> int:
    """Decorator returning a user ID for a JWT token as a parameter"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or " " not in auth_header:
        raise HTTPException(status_code=401, detail="Not authorized")
    token = auth_header.split()[1]
    data = decode_jwt(token)
    return data['id']


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_picture_util(file: UploadFile) -> str:
    """Generic method that uploads a photo, reduced size, reduced quality, jpg format, secure name, and returns the name of the image."""
    if not allowed_file(file.filename):
        raise ValueError("Unsupported file type")

    filename = f"{uuid4().hex}_{datetime.now().strftime('%d%m%Y-%H%M%S')}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    image = Image.open(file.file)
    if image.mode in ('RGBA', 'LA', 'P'):
        background = Image.new("RGB", image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
        image = background
    elif image.mode != 'RGB':
        image = image.convert("RGB")

    image.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
    image.save(filepath, "JPEG", quality=50, optimize=True)

    return filename


def get_version():
    """Retrieves the app version from version.txt (written by hands)"""
    try:
        with open("version.txt") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"
