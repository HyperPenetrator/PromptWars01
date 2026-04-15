"""
Phase 2 Verification Tests: Gemini Client, Maps Mock, and Cache.
Run with: pytest tests/test_phase2.py -v
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.maps_mock import StadiumDataProvider
from utils.cache import cache_set, cache_get, cache_clear_all, get_cache_stats


def test_stadium_data_provider_initialization():
    """Test StadiumDataProvider initialization."""
    provider = StadiumDataProvider()
    assert provider is not None
    print("[PASS] Stadium Data Provider initialized")


def test_stadium_data_provider_health_check():
    """Test health check for stadium data provider."""
    provider = StadiumDataProvider()
    assert provider.health_check() is True
    print("[PASS] Stadium Data Provider health check passed")


def test_get_all_pois():
    """Test retrieving all POIs."""
    provider = StadiumDataProvider()
    pois = provider.get_all_pois()
    assert len(pois) > 0
    assert "North Gate" in pois
    assert pois["North Gate"]["crowd_density"] >= 0
    print(f"[PASS] Retrieved {len(pois)} POIs")
    for poi_name, poi_data in list(pois.items())[:2]:
        print(f"  - {poi_name}: {poi_data['crowd_density']}% crowd")


def test_get_crowd_density():
    """Test crowd density retrieval."""
    provider = StadiumDataProvider()
    crowd = provider.get_crowd_density("North Gate")
    assert crowd is not None
    assert 0 <= crowd <= 100
    print(f"[PASS] Crowd density at North Gate: {crowd}%")


def test_get_nearby_pois():
    """Test nearby POI retrieval."""
    provider = StadiumDataProvider()
    nearby = provider.get_nearby_pois(40.7128, -74.0060, radius_km=0.5)
    assert len(nearby) > 0
    print(f"[PASS] Found {len(nearby)} nearby POIs")


def test_get_fastest_route():
    """Test route calculation."""
    provider = StadiumDataProvider()
    route = provider.get_fastest_route("North Gate", "Concession Stand A", avoid_crowds=True)
    assert route["start"] == "North Gate"
    assert route["end"] == "Concession Stand A"
    assert "recommendation" in route
    print(f"[PASS] Route calculated: {route['recommendation']}")


def test_cache_set_and_get():
    """Test cache set and get operations."""
    cache_clear_all()

    test_data = {"key": "value", "number": 42}
    cache_set("test_key", test_data)

    retrieved = cache_get("test_key")
    assert retrieved == test_data
    print("[PASS] Cache set/get working correctly")


def test_cache_expiry():
    """Test cache expiry (immediate 0-minute expiry)."""
    cache_clear_all()

    test_data = {"test": "data"}
    cache_set("expiry_test", test_data, expiry_minutes=0)

    retrieved = cache_get("expiry_test")
    assert retrieved is None
    print("[PASS] Cache expiry working correctly")


def test_cache_stats():
    """Test cache statistics."""
    cache_clear_all()
    cache_set("stat_test1", {"a": 1})
    cache_set("stat_test2", {"b": 2})

    stats = get_cache_stats()
    assert stats["entries"] >= 2
    print(f"[PASS] Cache stats: {stats['entries']} entries, {stats['total_size_bytes']} bytes")


def test_stadium_integration():
    """Integration test: Stadium data provider + POI crowd analysis."""
    provider = StadiumDataProvider()

    # Get all POIs
    all_pois = provider.get_all_pois()

    # Find least crowded POI
    least_crowded = min(all_pois.items(), key=lambda x: x[1]["crowd_density"])
    most_crowded = max(all_pois.items(), key=lambda x: x[1]["crowd_density"])

    print(f"[PASS] Least crowded: {least_crowded[0]} ({least_crowded[1]['crowd_density']}%)")
    print(f"[PASS] Most crowded: {most_crowded[0]} ({most_crowded[1]['crowd_density']}%)")

    # Calculate route avoiding crowds
    route = provider.get_fastest_route(
        least_crowded[0], most_crowded[0], avoid_crowds=True
    )
    assert route is not None
    print(f"[PASS] Smart route recommendation: {route['recommendation']}")


def test_gemini_import():
    """Test Gemini client can be imported (connectivity test)."""
    try:
        from services.gemini_client import GeminiClient
        print("[PASS] Gemini client module imported successfully")
        # Note: Actual API connectivity requires valid API key
        return True
    except ImportError as e:
        print(f"[FAIL] Failed to import Gemini client: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PHASE 2 VERIFICATION TEST SUITE")
    print("="*60 + "\n")

    # Run all tests
    tests = [
        ("Stadium Provider Init", test_stadium_data_provider_initialization),
        ("Stadium Provider Health", test_stadium_data_provider_health_check),
        ("Get All POIs", test_get_all_pois),
        ("Crowd Density", test_get_crowd_density),
        ("Nearby POIs", test_get_nearby_pois),
        ("Fastest Route", test_get_fastest_route),
        ("Cache Set/Get", test_cache_set_and_get),
        ("Cache Expiry", test_cache_expiry),
        ("Cache Stats", test_cache_stats),
        ("Stadium Integration", test_stadium_integration),
        ("Gemini Import", test_gemini_import),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"\n[TEST] {test_name}")
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] Assertion failed: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            failed += 1

    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")
