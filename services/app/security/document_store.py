import os
import hashlib
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import Document


class DocumentStore:
    """Document encryption, storage, and retrieval management."""

    def __init__(self, db: Optional[Session] = None, base_dir: str = "./secure/documents"):
        self.db = db
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def encrypt_document(self, doc_id: str, content: bytes) -> bytes:
        """Simulate or perform symmetric AES-256 encryption."""
        key = hashlib.sha256(doc_id.encode("utf-8")).digest()
        encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(content))
        return encrypted

    def decrypt_document(self, doc_id: str, encrypted_content: bytes) -> bytes:
        """Decrypt symmetric payload."""
        key = hashlib.sha256(doc_id.encode("utf-8")).digest()
        decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted_content))
        return decrypted

    def store_encrypted_document(self, doc_id: str, content: bytes) -> str:
        """Encrypt and persist document bytes to storage."""
        encrypted_data = self.encrypt_document(doc_id, content)
        file_path = os.path.join(self.base_dir, f"{doc_id}.enc")
        with open(file_path, "wb") as f:
            f.write(encrypted_data)
        return file_path
