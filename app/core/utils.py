from typing import Optional
import jwt
from fastapi import UploadFile, Request, Depends, HTTPException
from PIL import Image
import os
from datetime import datetime
from uuid import uuid4

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from app.core.config import settings


UPLOAD_FOLDER = "public/uploads/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

"""Retourne les valeurs décodées du token JWT"""
def decode_jwt(token: str):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

"""Retourne un user id pour un token JWT en paramètre"""
def get_user_id_from_jwt(request: Request) -> Optional[int]:
    auth_header = request.headers.get('Authorization')
    if not auth_header or " " not in auth_header:
        return None
    token = auth_header.split()[1]
    data = decode_jwt(token)
    if not data:
        return None
    return data['id']


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

"""Methode générique qui upload une photo, taille réduite, qualité réduite, format jpg, nom sécurisé et retourne le nom de l'image"""
def upload_picture_util(file: UploadFile) -> str:
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

"""
Nouvelle méthode à analyser..
async def upload_picture(file: UploadFile = File(...)):
    if not file.filename or '.' not in file.filename:
        raise HTTPException(status_code=400, detail="Invalid file")

    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Unsupported file type")

    filename = secure_filename(file.filename)
    suffix = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
    name_without_ext = os.path.splitext(filename)[0]
    new_filename = f"{name_without_ext}_{suffix}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, new_filename)

    if not filepath.startswith(UPLOAD_FOLDER):
        raise HTTPException(status_code=400, detail="Invalid file path")

    try:
        contents = await file.read()
        image = Image.open(BytesIO(contents))

        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        target_size = (1920, 1080)
        image.thumbnail(target_size, Image.Resampling.LANCZOS)
        image.save(filepath, 'JPEG', quality=50, optimize=True)

        return {"filename": new_filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while processing image: {str(e)}")
"""
