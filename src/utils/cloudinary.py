import cloudinary
from cloudinary.exceptions import Error as CloudinaryError
import cloudinary.uploader
from fastapi import UploadFile

from src.conf.config import settings
from src.exceptions import AvatarUploadError

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


def upload_avatar(file: UploadFile, public_id: str) -> str:
    try:
        result = cloudinary.uploader.upload(
            file.file,
            folder="contacts_api",
            public_id=public_id,
            overwrite=True,
        )
    except CloudinaryError as exc:
        raise AvatarUploadError(f"Cloudinary upload failed: {exc}") from exc

    return result["secure_url"]