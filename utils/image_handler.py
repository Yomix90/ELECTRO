from __future__ import annotations
import os
import uuid
from typing import Optional
from PIL import Image
from flask import current_app


ALLOWED = {"jpg", "jpeg", "png", "webp", "gif"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED


def save_product_image(file_storage, product_ref: str) -> Optional[str]:
    """
    Saves an uploaded image:
    - Validates extension
    - Generates a unique filename
    - Creates thumbnail (400x400) and large (1200x900) versions
    Returns the relative path stored in DB (e.g. 'products/LAP001_uuid.webp')
    or None on failure.
    """
    if not file_storage or not allowed_file(file_storage.filename):
        return None

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    products_dir = os.path.join(upload_dir, "products")
    os.makedirs(products_dir, exist_ok=True)

    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    uid = uuid.uuid4().hex[:8]
    base_name = f"{product_ref}_{uid}"
    filename = f"{base_name}.webp"  # Always convert to webp
    filepath = os.path.join(products_dir, filename)

    try:
        img = Image.open(file_storage.stream)
        img = img.convert("RGB")

        # Save large version
        large = img.copy()
        large.thumbnail(current_app.config["LARGE_SIZE"], Image.LANCZOS)
        large.save(filepath, "WEBP", quality=85, optimize=True)

        # Save thumbnail
        thumb_dir = os.path.join(products_dir, "thumbs")
        os.makedirs(thumb_dir, exist_ok=True)
        thumb = img.copy()
        thumb.thumbnail(current_app.config["THUMBNAIL_SIZE"], Image.LANCZOS)
        thumb.save(os.path.join(thumb_dir, filename), "WEBP", quality=80, optimize=True)

        return f"products/{filename}"
    except Exception as e:
        current_app.logger.error(f"Image save error: {e}")
        return None


def delete_product_image(relative_path: str):
    """Delete both the large image and its thumbnail."""
    if not relative_path:
        return
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    full_path = os.path.join(upload_dir, relative_path)
    thumb_path = os.path.join(upload_dir, relative_path.replace("products/", "products/thumbs/"))
    for path in [full_path, thumb_path]:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            current_app.logger.warning(f"Could not delete image {path}: {e}")


def get_thumbnail_path(relative_path: str) -> str:
    """Return the thumbnail path given a full image relative path."""
    if not relative_path:
        return ""
    return relative_path.replace("products/", "products/thumbs/")


def save_payment_proof(file_storage, sale_ref: str) -> Optional[str]:
    """
    Saves an uploaded payment proof (image or PDF):
    - Validates extension
    - Generates a unique filename
    - Saves it in 'static/uploads/payments/'
    Returns the relative path stored in DB (e.g. 'payments/proof_VNT-0001_uuid.jpg')
    or None on failure.
    """
    if not file_storage:
        return None

    filename = file_storage.filename
    if not filename or "." not in filename:
        return None

    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in {"jpg", "jpeg", "png", "webp", "gif", "pdf"}:
        return None

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    payments_dir = os.path.join(upload_dir, "payments")
    os.makedirs(payments_dir, exist_ok=True)

    uid = uuid.uuid4().hex[:8]
    clean_ref = "".join(c for c in sale_ref if c.isalnum() or c in "-_").strip()
    new_filename = f"proof_{clean_ref}_{uid}.{ext}"
    filepath = os.path.join(payments_dir, new_filename)

    try:
        file_storage.save(filepath)
        return f"payments/{new_filename}"
    except Exception as e:
        current_app.logger.error(f"Payment proof save error: {e}")
        return None

