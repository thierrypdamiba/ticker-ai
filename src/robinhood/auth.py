import os
import base64
import hashlib
import hmac
import time
import json
from typing import Optional
import logging

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

class RobinhoodAuthenticator:
    """
    Handles Robinhood API authentication using Ed25519 signatures.
    """

    def __init__(self, private_key_pem: Optional[str] = None, private_key_path: Optional[str] = None):
        """
        Initializes the authenticator with either a private key string or a path to a PEM file.

        Args:
            private_key_pem: The private key in PEM format as a string.
            private_key_path: The path to the private key PEM file.
        """
        self.private_key = self._load_private_key(private_key_pem, private_key_path)

    def _load_private_key(self, private_key_pem: Optional[str], private_key_path: Optional[str]) -> ed25519.Ed25519PrivateKey:
        """
        Loads the Ed25519 private key from either a PEM string or a file.

        Args:
            private_key_pem: The private key in PEM format as a string.
            private_key_path: The path to the private key PEM file.

        Returns:
            The loaded Ed25519 private key.

        Raises:
            ValueError: If neither private_key_pem nor private_key_path is provided,
                        or if both are provided.
            FileNotFoundError: If the private key file is not found.
            Exception: If there's an error during key loading.
        """
        if private_key_pem and private_key_path:
            raise ValueError("Provide either private_key_pem or private_key_path, not both.")

        if not private_key_pem and not private_key_path:
            raise ValueError("Either private_key_pem or private_key_path must be provided.")

        try:
            if private_key_pem:
                private_key = serialization.load_pem_private_key(
                    private_key_pem.encode('utf-8'),
                    password=None,
                    backend=default_backend()
                )
            else:  # private_key_path is provided
                with open(private_key_path, "rb") as key_file:
                    private_key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=None,
                        backend=default_backend()
                    )
            return private_key

        except FileNotFoundError as e:
            logger.error(f"Private key file not found: {e}")
            raise
        except Exception as e:
            logger.exception(f"Error loading private key: {e}")
            raise

    def generate_signature(self, message: str) -> str:
        """
        Generates an Ed25519 signature for the given message.

        Args:
            message: The message to sign.

        Returns:
            The base64-encoded Ed25519 signature.
        """
        try:
            signature = self.private_key.sign(message.encode('utf-8'))
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            logger.exception(f"Error generating signature: {e}")
            raise

    def get_auth_headers(self, method: str, path: str, body: Optional[str] = None) -> dict:
        """
        Generates the authentication headers for a Robinhood API request.

        Args:
            method: The HTTP method (e.g., "GET", "POST").
            path: The API endpoint path (e.g., "/orders").
            body: The request body, if any (as a string).

        Returns:
            A dictionary containing the authentication headers.
        """
        timestamp = str(int(time.time()))
        message = f"{timestamp}{method}{path}"
        if body:
            message += body

        signature = self.generate_signature(message)

        headers = {
            "RH-Timestamp": timestamp,
            "RH-Signature": signature,
        }
        return headers