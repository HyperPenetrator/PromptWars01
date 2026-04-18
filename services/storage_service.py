"""
Enterprise Firebase/Firestore Service for StadiumFlow AI.
Handles persistence of navigation decisions and crowd telemetry.
"""

import logging
from typing import Dict, Any, Optional
from google.cloud import firestore
from utils.config import AppConfig

logger = logging.getLogger(__name__)


class FirestoreService:
    """
    Native GCP Firestore integration for stadium event state management.
    """

    def __init__(self, project_id: Optional[str] = None) -> None:
        """Initializes the Firestore client."""
        self.project_id = project_id or AppConfig.PROJECT_ID
        try:
            self.db = firestore.Client(project=self.project_id)
            logger.info("🔥 Firestore Service: CONNECTED")
        except Exception as e:
            logger.warning(f"🔥 Firestore connection failed: {e}. Using mock state.")
            self.db = None

    def save_decision(self, session_id: str, decision_data: Dict[str, Any]) -> bool:
        """
        Persists a navigation decision to the 'navigation_history' collection.
        """
        if not self.db:
            return False
            
        try:
            doc_ref = self.db.collection("navigation_history").document(session_id)
            doc_ref.set({
                **decision_data,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            logger.info(f"✅ Decision persisted to Firestore: {session_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Firestore write error: {str(e)}")
            return False

    def get_stadium_state(self) -> Dict[str, Any]:
        """
        Retrieves global stadium status from the 'infrastructure' collection.
        """
        if not self.db:
            return {"status": "OFFLINE", "crowd_avg": 0}
            
        try:
            doc = self.db.collection("infrastructure").document("live_status").get()
            return doc.to_dict() if doc.exists else {"status": "STABLE", "crowd_avg": 45}
        except Exception:
            return {"status": "STABLE", "crowd_avg": 45}
