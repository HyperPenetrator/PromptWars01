"""
Service Integration Tests for StadiumFlow AI.
Verifies mock data integrity and configuration logic.
"""

import pytest
from services.maps_mock import StadiumDataProvider
from services.storage_service import FirestoreService
from services.spatial_service import SpatialService
from utils.config import AppConfig

def test_stadium_data_integrity():
    """Verifies the stadium data provider returns valid spatial manifests."""
    provider = StadiumDataProvider()
    pois = provider.get_all_pois()
    
    assert len(pois) > 0
    assert "North Gate" in pois
    assert "crowd_density" in pois["North Gate"]
    assert provider.health_check() is True

def test_firestore_service_instantiation():
    """Verifies Firestore service can be instantiated and handles missing GCP env."""
    storage = FirestoreService(project_id="test-project")
    # Even if real GCP fails, it should gracefully fall back to mockable state
    assert hasattr(storage, 'db')

def test_spatial_service_logic():
    """Verifies Google Maps spatial logic with mock/fallback."""
    spatial = SpatialService(api_key="AIzaTest")
    eta = spatial.get_precise_eta("Gate A", "Gate B")
    assert isinstance(eta, int)
    assert eta > 0

def test_config_logic():
    """Verifies that AppConfig correctly identifies project environment."""
    # Location should default if not set
    assert AppConfig.LOCATION in ["us-central1", "global"]
    
    # Check production flag consistency
    if AppConfig.STADIUM_ENV == "production":
        assert AppConfig.is_production() is True
    else:
        assert AppConfig.is_production() is False
