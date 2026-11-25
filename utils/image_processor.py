"""
Utility: Image processing for pest/disease detection
"""
import base64
import os
from PIL import Image
import io


def process_uploaded_image(file_storage) -> tuple[str, str]:
    """
    Process an uploaded image file.
    Returns (base64_string, error_message).
    """
    try:
        # Read and validate image
        img_bytes = file_storage.read()
        img = Image.open(io.BytesIO(img_bytes))

        # Resize if too large to stay within token limits
        max_dim = 1024
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # Convert to RGB (handles RGBA, palette modes)
        if img.mode not in ("RGB",):
            img = img.convert("RGB")

        # Re-encode as JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode("utf-8")
        return b64, None

    except Exception as e:
        return None, str(e)


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )


def save_upload(file_storage, upload_folder: str) -> str:
    """Save uploaded file and return the saved filename."""
    from werkzeug.utils import secure_filename
    import uuid
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_folder, filename)
    file_storage.seek(0)
    file_storage.save(filepath)
    return filename
