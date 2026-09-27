import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'md', 'csv', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 Megabytes

def allowed_file(filename: str) -> bool:
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def get_file_type(filename: str) -> str:
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext == 'pdf':
        return 'pdf'
    elif ext in {'png', 'jpg', 'jpeg'}:
        return 'image'
    elif ext in {'txt', 'md', 'csv'}:
        return 'text'
    return 'document'

def extract_text_from_file(file_path: str, ext: str) -> str:
    """Extracts text content from given file path based on extension."""
    ext = ext.lower()
    extracted_chunks = []

    if ext == 'pdf':
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ''
                text = text.strip()
                if text:
                    extracted_chunks.append(f"--- Page {page_idx + 1} ---\n{text}")
            return "\n\n".join(extracted_chunks).strip()
        except Exception as e:
            return f"[Notice: PDF text extraction encountered an error: {str(e)}]"

    elif ext in {'txt', 'md', 'csv'}:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1', errors='replace') as f:
                return f.read().strip()
        except Exception as e:
            return f"[Notice: Text file read error: {str(e)}]"

    elif ext in {'png', 'jpg', 'jpeg'}:
        basename = os.path.basename(file_path)
        return f"[Image Document: {basename}. Contains visual study notes/diagrams.]"

    return ""

def generate_snippet(text: str, max_chars: int = 220) -> str:
    if not text:
        return "No text could be extracted from this document."
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars].rstrip() + "..."

def process_uploaded_document(file_storage, user_id: str, upload_root: str = 'uploads/documents') -> dict:
    """
    Validates, securely stores, and extracts text from an uploaded file.
    Returns metadata dict ready for Document model persistence.
    """
    if not file_storage or not file_storage.filename:
        raise ValueError("No file provided.")

    original_filename = file_storage.filename
    if not allowed_file(original_filename):
        raise ValueError(f"File type not supported. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    # Determine extension and sanitized filename
    ext = original_filename.rsplit('.', 1)[1].lower()
    safe_name = secure_filename(original_filename)
    if not safe_name:
        safe_name = f"upload_{uuid.uuid4().hex[:8]}.{ext}"

    # Target directory per user
    user_upload_dir = os.path.join(upload_root, str(user_id))
    os.makedirs(user_upload_dir, exist_ok=True)

    unique_filename = f"{uuid.uuid4().hex[:8]}_{safe_name}"
    destination_path = os.path.join(user_upload_dir, unique_filename)

    # Save to disk
    file_storage.save(destination_path)
    file_size = os.path.getsize(destination_path)

    if file_size > MAX_FILE_SIZE:
        try:
            os.remove(destination_path)
        except OSError:
            pass
        raise ValueError("File exceeds maximum allowed size of 15MB.")

    # Extract text content
    extracted_text = extract_text_from_file(destination_path, ext)
    summary = generate_snippet(extracted_text)

    return {
        "filename": original_filename,
        "file_path": destination_path,
        "file_type": get_file_type(original_filename),
        "file_size": file_size,
        "extracted_text": extracted_text,
        "summary": summary
    }
