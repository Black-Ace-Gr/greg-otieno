"""Cloudinary-backed storage for uploaded photos and documents.

Active only when the CLOUDINARY_URL environment variable is set; otherwise files
are saved to the local media folder (handy for development).
"""
import io
import os
import uuid
from urllib.parse import quote

from django.core.files.storage import FileSystemStorage, Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class CloudinaryStorage(Storage):
    def __init__(self, resource_type="image"):
        self.resource_type = resource_type  # "image" or "raw"

    def _save(self, name, content):
        import cloudinary.uploader

        stem, ext = os.path.splitext(name.replace("\\", "/"))
        unique = uuid.uuid4().hex[:8]
        # Raw files keep their extension inside the public id; images do not.
        public_id = f"{stem}_{unique}{ext}" if self.resource_type == "raw" else f"{stem}_{unique}"
        content.seek(0)
        result = cloudinary.uploader.upload(
            io.BytesIO(content.read()),
            public_id=public_id,
            resource_type=self.resource_type,
            overwrite=False,
        )
        if self.resource_type == "raw":
            return result["public_id"]
        return f'{result["public_id"]}.{result["format"]}'

    def url(self, name):
        import cloudinary

        cloud = cloudinary.config().cloud_name
        return f"https://res.cloudinary.com/{cloud}/{self.resource_type}/upload/{quote(name)}"

    def exists(self, name):
        return False  # names are made unique on save

    def delete(self, name):
        import cloudinary.uploader

        public_id = name if self.resource_type == "raw" else os.path.splitext(name)[0]
        try:
            cloudinary.uploader.destroy(public_id, resource_type=self.resource_type)
        except Exception:
            pass

    def _open(self, name, mode="rb"):
        raise NotImplementedError("Files are served directly from Cloudinary.")


def _use_cloudinary():
    return bool(os.environ.get("CLOUDINARY_URL"))


def image_storage():
    return CloudinaryStorage("image") if _use_cloudinary() else FileSystemStorage()


def raw_storage():
    return CloudinaryStorage("raw") if _use_cloudinary() else FileSystemStorage()