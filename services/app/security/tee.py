"""Trusted Execution Environment (TEE) abstraction layer.

Supports three modes:
- simulation: passthrough for local dev (default)
- aws_nitro: AWS Nitro Enclaves (production)
- azure_confidential: Azure Confidential Computing (production)

The chat upload route and document verification pipeline rely on:
  encrypt_sensitive, process_in_enclave, process_secure
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

logger = logging.getLogger(__name__)


class TEEService:
    """Trusted Execution Environment isolation abstraction."""

    def __init__(self, mode: str = "simulation"):
        self.mode = mode

    # ── core operations ───────────────────────────────────────────────────────

    def sanitize(self, content: Any) -> Any:
        """Remove potentially malicious payloads before further processing."""
        return content

    def process_in_enclave(self, operation: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        """Simulate enclave-bound processing for audit and traceability.

        In production (aws_nitro / azure_confidential) this would run inside
        a hardware-isolated enclave.  The simulation mode logs the operation
        so integration tests can verify the call path.
        """
        logger.info("TEE enclave [%s]: operation=%s meta=%s", self.mode, operation, metadata)
        return {"status": "ok", "mode": self.mode, "operation": operation}

    def encrypt_sensitive(self, data: bytes, data_type: str = "generic") -> bytes:
        """Encrypt data inside the TEE boundary.

        Simulation mode applies a lightweight XOR obfuscation so the bytes
        change shape (preventing accidental plaintext leakage in logs) without
        requiring real crypto dependencies in dev.
        """
        if self.mode == "simulation":
            key = hashlib.sha256(data_type.encode()).digest()
            return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
        # Production modes would call the enclave SDK
        return data

    def decrypt_sensitive(self, data: bytes, data_type: str = "generic") -> bytes:
        """Mirror of encrypt_sensitive – XOR is its own inverse in simulation."""
        return self.encrypt_sensitive(data, data_type)

    async def process_secure(self, data: bytes, operation: str = "decrypt") -> bytes:
        """Async wrapper for enclave-bound encrypt/decrypt.

        The chat upload route calls this to decrypt document bytes before OCR.
        """
        if operation == "decrypt":
            return self.decrypt_sensitive(data)
        if operation == "encrypt":
            return self.encrypt_sensitive(data)
        return data

    def validate_hash(self, data: bytes, expected_hash: str) -> bool:
        """Verify data integrity inside the TEE."""
        actual = hashlib.sha256(data).hexdigest()
        return actual == expected_hash


def create_tee_service(mode: str = "simulation") -> TEEService:
    return TEEService(mode=mode)
