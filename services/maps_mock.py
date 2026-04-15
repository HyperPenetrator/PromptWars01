"""
Mock Google Maps Service for Stadium Data.
Simulates live stadium crowd density and POI location data.
"""

import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StadiumDataProvider:
    """Mock provider for stadium crowd density and POI data."""

    # Simulated stadium layout with POIs
    STADIUM_POIS = {
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
    CROWD_ZONES = {
        "North Gate": 45,
        "Concession Stand A": 78,
        "Concession Stand B": 32,
        "First Aid Station": 5,
        "Restroom Hub": 85,
        "Merchandise Booth": 60,
    }

    def __init__(self) -> None:
        """Initialize the mock stadium data provider."""
        logger.info("✓ Stadium data provider initialized")

    def get_nearby_pois(
        self, user_lat: float, user_lng: float, radius_km: float = 0.5
    ) -> list[dict]:
        """
        Get POIs near user location (simulated).

        Args:
            user_lat: User's latitude.
            user_lng: User's longitude.
            radius_km: Search radius in kilometers.

        Returns:
            List of nearby POIs with location and crowd data.
        """
        pois = []
        for name, coords in self.STADIUM_POIS.items():
            crowd = self.CROWD_ZONES.get(name, 50)
            pois.append(
                {
                    "name": name,
                    "lat": coords["lat"],
                    "lng": coords["lng"],
                    "type": coords["type"],
                    "crowd_density": crowd,
                    "status": "open" if crowd < 95 else "crowded",
                }
            )
        logger.info(f"✓ Retrieved {len(pois)} nearby POIs")
        return pois

    def get_crowd_density(self, location_name: str) -> Optional[int]:
        """
        Get current crowd density for a location.

        Args:
            location_name: Name of the location/POI.

        Returns:
            Crowd density as integer (0-100), or None if not found.
        """
        density = self.CROWD_ZONES.get(location_name)
        if density is not None:
            logger.info(f"✓ Crowd density at {location_name}: {density}%")
            return density
        logger.warning(f"✗ Location '{location_name}' not found")
        return None

    def get_fastest_route(
        self, start_location: str, end_location: str, avoid_crowds: bool = True
    ) -> dict:
        """
        Calculate fastest route considering crowd density.

        Args:
            start_location: Starting POI name.
            end_location: Destination POI name.
            avoid_crowds: If True, prefer less crowded routes.

        Returns:
            Route info with estimated duration and crowd impact.
        """
        start_crowd = self.CROWD_ZONES.get(start_location, 50)
        end_crowd = self.CROWD_ZONES.get(end_location, 50)

        if avoid_crowds and end_crowd > 80:
            recommendation = "High crowd at destination - consider alternatives"
        elif avoid_crowds and end_crowd < 30:
            recommendation = "Low crowd - optimal for quick access"
        else:
            recommendation = "Moderate crowd - standard travel time"

        route = {
            "start": start_location,
            "end": end_location,
            "start_crowd": start_crowd,
            "end_crowd": end_crowd,
            "estimated_minutes": 5,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat(),
        }
        logger.info(f"✓ Route calculated: {start_location} → {end_location}")
        return route

    def get_all_pois(self) -> dict:
        """
        Get all stadium POIs with current crowd data.

        Returns:
            Dictionary of all POIs with their current status.
        """
        pois_with_status = {}
        for name, coords in self.STADIUM_POIS.items():
            crowd = self.CROWD_ZONES.get(name, 50)
            pois_with_status[name] = {
                **coords,
                "crowd_density": crowd,
                "status": "open" if crowd < 95 else "crowded",
            }
        logger.info(f"✓ Retrieved all {len(pois_with_status)} POIs")
        return pois_with_status

    def health_check(self) -> bool:
        """
        Verify stadium data provider is functional.

        Returns:
            True if data provider is working.
        """
        try:
            pois = self.get_all_pois()
            if pois:
                logger.info("✓ Stadium data provider health check passed")
                return True
        except Exception as e:
            logger.error(f"✗ Health check failed: {str(e)}")
        return False
