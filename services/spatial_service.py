"""
Enterprise Google Maps Spatial Service for StadiumFlow AI.
Handles high-fidelity geocoding and pathfinding for stadium venues.
"""

import logging
from typing import List, Dict, Any, Optional
import googlemaps
from utils.config import AppConfig

logger = logging.getLogger(__name__)


class SpatialService:
    """
    Native Google Maps Platform integration for stadium navigation.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initializes the Google Maps client."""
        self.api_key = api_key or AppConfig.GEMINI_API_KEY # Sharing key if configured for both
        try:
            self.gmaps = googlemaps.Client(key=self.api_key)
            logger.info("🗺️ Google Maps Service: INITIALIZED")
        except Exception as e:
            logger.warning(f"🗺️ Google Maps init failed: {e}. Using mock spatial engine.")
            self.gmaps = None

    def get_precise_eta(self, origin: str, destination: str) -> int:
        """
        Calculates precise travel time using Distance Matrix API.
        """
        if not self.gmaps:
            return 5 # Default mock
            
        try:
            matrix = self.gmaps.distance_matrix(origin, destination, mode="walking")
            if matrix["status"] == "OK":
                duration_sec = matrix["rows"][0]["elements"][0]["duration"]["value"]
                return max(1, duration_sec // 60)
        except Exception:
            pass
        return 5

    def get_venue_poi(self, venue_name: str, query: str) -> List[Dict[str, Any]]:
        """
        Finds points of interest within a stadium using Places API.
        """
        if not self.gmaps:
            return []
            
        try:
            results = self.gmaps.places(query=f"{query} inside {venue_name}")
            return results.get("results", [])
        except Exception as e:
            logger.error(f"❌ Places API error: {str(e)}")
            return []
