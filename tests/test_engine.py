"""
Comprehensive Test Suite for StadiumFlow AI Engine.
Covers core reasoning, suitability scoring, and decision quality metrics.
"""

import pytest
from core.engine import SmartAssistant, UserContext, DecisionQuality
from services.maps_mock import StadiumDataProvider

class MockGemini:
    """Mock for Vertex AI client to test engine logic without API calls."""
    def analyze_crowd_density(self, location, crowd_level, poi_list):
        return "Mocked AI Reasoning: Success"
    def health_check(self):
        return True

@pytest.fixture
def engine():
    """Provides a fresh SmartAssistant instance for each test."""
    gemini = MockGemini()
    stadium = StadiumDataProvider()
    return SmartAssistant(gemini, stadium)

def test_suitability_score_calculation(engine):
    """Verifies that suitability scoring penalizes crowds correctly."""
    # Low crowd (10%), Low urgency (1) -> Should be high score
    score_low = engine._evaluate_poi_suitability("Test POI", 10, 1)
    
    # High crowd (90%), High urgency (5) -> Should be very low score
    score_high = engine._evaluate_poi_suitability("Test POI", 90, 5)
    
    assert score_low > 0.8
    assert score_high < 0.2
    assert 0.0 <= score_low <= 1.0
    assert 0.0 <= score_high <= 1.0

def test_decision_quality_assessment(engine):
    """Verifies the logic for OPTIMAL vs SUBOPTIMAL decisions."""
    # Big gap, high top score -> OPTIMAL
    quality_opt = engine._assess_decision_quality(0.95, 0.6)
    assert quality_opt == DecisionQuality.OPTIMAL
    
    # Small gap, low top score -> SUBOPTIMAL
    quality_sub = engine._assess_decision_quality(0.4, 0.38)
    assert quality_sub == DecisionQuality.SUBOPTIMAL

def test_reason_navigation_flow(engine):
    """Verifies the end-to-end reasoning flow for a user request."""
    context = UserContext(
        current_location="North Gate",
        destination_type="concession",
        current_time="12:00",
        urgency_level=3
    )
    
    decision = engine.reason_navigation(context)
    
    assert decision.recommended_poi is not None
    assert len(decision.reasoning_steps) >= 6
    assert "AI Analysis: Mocked AI Reasoning: Success" in decision.reasoning_steps[3]
    assert decision.confidence_score > 0
    assert isinstance(decision.decision_quality, DecisionQuality)

def test_crowd_risk_labels(engine):
    """Ensures crowd risk categorization is accurate."""
    assert engine._get_crowd_risk_label(10) == "low"
    assert engine._get_crowd_risk_label(50) == "medium"
    assert engine._get_crowd_risk_label(90) == "high"
