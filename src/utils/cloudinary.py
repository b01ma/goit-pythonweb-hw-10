import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from src.conf.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


def upload_avatar(file: UploadFile, public_id: str) -> str:
    result = cloudinary.uploader.upload(
        file.file,
        folder="contacts_api",
        public_id=public_id,
        overwrite=True,
    )
    return result["secure_url"]