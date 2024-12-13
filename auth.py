"""
Authentication module for the stock importer application.

Have this handle user auth and credential management.
"""
import logging
from typing import Tuple
from pathlib import Path
from config import CREDENTIALS_FILE, DEFAULT_USERNAME, DEFAULT_PASSWORD

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass

class CredentialManager:
    """Manages user credentials and authentication."""

    @staticmethod
    def verify_credentials(username: str, password: str) -> bool:
        """
        Verify login credentials.

        Args:
            username: Username to verify
            password: Password to verify

        Returns:
            True if credentials are valid, False otherwise
        """
        logger.debug(f"Verifying credentials for user: {username}")

        # Clean up input
        username = username.strip().lower()

        # Get credential file path from current module
        cred_file = Path(CREDENTIALS_FILE)
        logger.debug(f"Checking for credentials file: {cred_file} (absolute: {cred_file.absolute()})")

        # If file doesn't exist, use default credentials
        if not cred_file.exists():
            logger.debug("No credentials file found, using default credentials")
            result = (username == DEFAULT_USERNAME.lower() and
                     password == DEFAULT_PASSWORD)
            logger.debug(f"Default credentials validation result: {result}")
            return result

        # If file exists, verify against stored credentials
        try:
            stored_username, stored_password = CredentialManager.load_credentials()
            logger.debug("Using stored credentials for verification")
            result = (username == stored_username.lower() and
                     password == stored_password)
            logger.debug(f"Stored credentials validation result: {result}")
            return result
        except FileNotFoundError:
            # Handle race condition where file might be deleted
            logger.debug("Credentials file not found (race condition), using defaults")
            return (username == DEFAULT_USERNAME.lower() and
                   password == DEFAULT_PASSWORD)
        except Exception as e:
            logger.error(f"Error verifying credentials: {e}")
            return False

    @staticmethod
    def save_credentials(username: str, password: str) -> None:
        """
        Save credentials to file.

        Args:
            username: Username to save
            password: Password to save
        """
        try:
            # Create parent directory if it doesn't exist
            cred_file = Path(CREDENTIALS_FILE)
            cred_file.parent.mkdir(parents=True, exist_ok=True)

            # Save credentials
            with open(cred_file, "w") as file:
                file.write(f"{username.strip()}\n{password}")
            logger.info("Credentials saved successfully")
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            raise

    @staticmethod
    def load_credentials() -> Tuple[str, str]:
        """
        Load credentials from file.

        Returns:
            Tuple of (username, password)

        Raises:
            FileNotFoundError: If credentials file doesn't exist
            ValueError: If credentials file is invalid
        """
        try:
            with open(CREDENTIALS_FILE, "r") as file:
                lines = file.read().strip().split("\n")
                if len(lines) != 2:
                    raise ValueError("Invalid credentials file format")
                return lines[0].strip(), lines[1]
        except FileNotFoundError:
            logger.warning("No credentials file found")
            raise
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            raise