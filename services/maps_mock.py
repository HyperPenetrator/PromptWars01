"""
Mock Google Maps Service for Stadium Data.
Simulates live stadium crowd density and POI location data.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class StadiumDataProvider:
    """
    Enterprise Mock Provider for stadium spatial and crowd analytics.
    Simulates high-fidelity telemetry from IoT sensors across the stadium infrastructure.
    """

    # Simulated stadium layout with POIs
    STADIUM_POIS: Dict[str, Dict[str, Any]] = {
        "North Gate": {"lat": 40.7128, "lng": -74.0060, "type": "entrance"},
        "Concession Stand A": {
            "lat": 40.7130,
            "lng": -74.0062,
            "type": "concession",
        },
        "Concession Stand B": {
            "lat": 40.7126,
            "lng": -74.0058,
            "type": "concession",
        },
        "First Aid Station": {"lat": 40.7129, "lng": -74.0061, "type": "medical"},
        "Restroom Hub": {"lat": 40.7127, "lng": -74.0059, "type": "restroom"},
        "Merchandise Booth": {
            "lat": 40.7125,
            "lng": -74.0063,
            "type": "merchandise",
        },
    }

    # Simulated crowd density zones (0-100 scale)
    CROWD_ZONES: Dict[str, int] = {
        "North Gate": 45,
        "Concession Stand A": 78,
        "Concession Stand B": 32,
        "First Aid Station": 5,
        "Restroom Hub": 85,
        "Merchandise Booth": 60,
    }

    def __init__(self) -> None:
        """Initializes the stadium spatial data provider."""
        logger.info("📡 Stadium Telemetry Provider: ONLINE")

    def get_nearby_pois(
        self, user_lat: float, user_lng: float, radius_km: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Retrieves Points of Interest within a specified spatial radius.

        Args:
            user_lat: Latitude of the observer.
            user_lng: Longitude of the observer.
            radius_km: Spatial search radius in kilometers.

        Returns:
            List of POI metadata dictionaries including live crowd density.
        """
        pois: List[Dict[str, Any]] = []
        for name, coords in self.STADIUM_POIS.items():
            crowd = self.CROWD_ZONES.get(name, 50)
            pois.append(
                {
                    "name": name,
                    "lat": coords["lat"],
                    "lng": coords["lng"],
                    "type": coords["type"],
                    "crowd_density": crowd,
                    "status": "OPTIMAL" if crowd < 50 else "STRESSED" if crowd < 85 else "CAPACITY",
                }
            )
        return pois

    def get_crowd_density(self, location_name: str) -> Optional[int]:
        """
        Fetches the real-time crowd percentage for a specific stadium zone.

        Args:
            location_name: Unique identifier for the stadium zone.

        Returns:
            Integer percentage (0-100) or None if zone telemetry is unavailable.
        """
        return self.CROWD_ZONES.get(location_name)

    def get_fastest_route(
        self, start_location: str, end_location: str, avoid_crowds: bool = True
    ) -> Dict[str, Any]:
        """
        Calculates the optimal navigational path between two stadium nodes.

        Args:
            start_location: Origin node ID.
            end_location: Destination node ID.
            avoid_crowds: Flag to prioritize low-density paths.

        Returns:
            Dictionary containing route metadata and AI-ready recommendations.
        """
        end_crowd = self.CROWD_ZONES.get(end_location, 50)
        
        recommendation = (
            "CRITICAL: High congestion at destination." if end_crowd > 80 
            else "OPTIMAL: Minimal crowd interference." if end_crowd < 30
            else "STABLE: Moderate pedestrian flow."
        )

        return {
            "start": start_location,
            "end": end_location,
            "end_crowd_percentage": end_crowd,
            "estimated_minutes": 5 + (end_crowd // 20),
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat(),
        }

    def get_all_pois(self) -> Dict[str, Any]:
        """
        Aggregates all stadium POIs into a single spatial manifest.

        Returns:
            Dictionary of all POIs with nested telemetry data.
        """
        return {
            name: {
                **coords,
                "crowd_density": self.CROWD_ZONES.get(name, 50),
                "status": "STABLE" if self.CROWD_ZONES.get(name, 0) < 70 else "CONGESTED",
            } for name, coords in self.STADIUM_POIS.items()
        }

    def health_check(self) -> bool:
        """Verifies integrity of the stadium telemetry service."""
        if len(self.STADIUM_POIS) > 0:
            return True
        return False
