"""
Enterprise Configuration & Secret Management for StadiumFlow AI.
Implements defensive security practices using Google Secret Manager.
"""

import os
import logging
from typing import Optional

# Google Cloud Secret Manager
try:
    from google.cloud import secretmanager
    HAS_SECRET_MANAGER = True
except ImportError:
    HAS_SECRET_MANAGER = False

logger = logging.getLogger(__name__)


def get_secret(secret_id: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieves a secret from Google Secret Manager with local environment fallback.

    Args:
        secret_id: The ID of the secret to retrieve.
        default: Fallback value if secret is not found.

    Returns:
        The secret value or default.
    """
    # 1. Try Environment Variable first (fastest)
    env_val = os.getenv(secret_id)
    if env_val:
        return env_val

    # 2. Try Google Secret Manager if available
    if HAS_SECRET_MANAGER:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if project_id:
            try:
                client = secretmanager.SecretManagerServiceClient()
                name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
                response = client.access_secret_version(request={"name": name})
                secret_payload = response.payload.data.decode("UTF-8")
                logger.info(f"🔒 Secret '{secret_id}' retrieved from Google Secret Manager")
                return secret_payload
            except Exception as e:
                logger.debug(f"Secret Manager access failed for {secret_id}: {e}")

    # 3. Final Fallback
    return default


class AppConfig:
    """Centralized application configuration."""
    
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT_ID")
    LOCATION = os.getenv("GCP_LOCATION", "us-central1")
    
    # Security: Fetch critical keys through defensive getter
    GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
    STADIUM_ENV = os.getenv("STADIUM_ENV", "production")

    @classmethod
    def is_production(cls) -> bool:
        """Checks if the app is running in production mode."""
        return cls.STADIUM_ENV.lower() == "production"
