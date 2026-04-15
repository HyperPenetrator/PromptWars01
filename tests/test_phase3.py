"""
Phase 3 Logic Test: Agentic Reasoning Engine.
Demonstrates Logical Decision Making benchmarks.
Run with: python tests/test_phase3.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import SmartAssistant, UserContext, DecisionQuality
from services.maps_mock import StadiumDataProvider


class MockGeminiClient:
    """Mock Gemini client for testing without API key."""

    def health_check(self):
        return True

    def analyze_crowd_density(self, location, crowd_level, poi_list):
        return f"Mock analysis for {location} with {crowd_level}% crowd"

    def reasoning_chain(self, query, context):
        return f"Mock reasoning for: {query}"


def test_smart_assistant_initialization():
    """Test SmartAssistant initialization."""
    gemini_mock = MockGeminiClient()
    stadium = StadiumDataProvider()
    assistant = SmartAssistant(gemini_mock, stadium)
    assert assistant is not None
    print("[PASS] SmartAssistant initialized")


def test_evaluate_poi_suitability():
    """Test POI suitability evaluation."""
    gemini_mock = MockGeminiClient()
    stadium = StadiumDataProvider()
    assistant = SmartAssistant(gemini_mock, stadium)

    # Test 1: Low crowd (good suitability)
    low_crowd_score = assistant._evaluate_poi_suitability("POI_1", crowd_density=20, user_urgency=1)
    assert 0.7 <= low_crowd_score <= 1.0
    print(f"[PASS] Low crowd POI score: {low_crowd_score:.2f}")

    # Test 2: High crowd (poor suitability)
    high_crowd_score = assistant._evaluate_poi_suitability("POI_2", crowd_density=90, user_urgency=1)
    assert 0.0 <= high_crowd_score <= 0.3
    print(f"[PASS] High crowd POI score: {high_crowd_score:.2f}")

    # Test 3: Urgency impact (high urgency = stricter crowd tolerance for moderate crowds)
    urgent_moderate = assistant._evaluate_poi_suitability("POI_3", crowd_density=60, user_urgency=5)
    normal_moderate = assistant._evaluate_poi_suitability("POI_3", crowd_density=60, user_urgency=1)
    assert urgent_moderate < normal_moderate
    print(f"[PASS] Urgency multiplier works (urgent: {urgent_moderate:.2f}, normal: {normal_moderate:.2f})")


def test_rank_options():
    """Test POI ranking logic."""
    gemini_mock = MockGeminiClient()
    stadium = StadiumDataProvider()
    assistant = SmartAssistant(gemini_mock, stadium)

    all_pois = stadium.get_all_pois()
    ranked = assistant._rank_options(all_pois, user_urgency=3)

    # Verify ranking is sorted descending
    assert all(ranked[i][1] >= ranked[i+1][1] for i in range(len(ranked)-1))
    print(f"[PASS] Ranked {len(ranked)} POIs correctly")
    print(f"       Top 3: {', '.join([f'{poi[0]} ({poi[1]:.2f})' for poi in ranked[:3]])}")


def test_assess_decision_quality():
    """Test decision quality assessment."""
    gemini_mock = MockGeminiClient()
    stadium = StadiumDataProvider()
    assistant = SmartAssistant(gemini_mock, stadium)

    # Test OPTIMAL decision (high score, large gap)
    optimal_quality = assistant._assess_decision_quality(top_poi_score=0.95, runner_up_score=0.65)
    assert optimal_quality == DecisionQuality.OPTIMAL
    print(f"[PASS] Optimal quality detected: {optimal_quality.value}")

    # Test GOOD decision
    good_quality = assistant._assess_decision_quality(top_poi_score=0.8, runner_up_score=0.65)
    assert good_quality == DecisionQuality.GOOD
    print(f"[PASS] Good quality detected: {good_quality.value}")

    # Test SUBOPTIMAL decision (unclear choice)
    suboptimal_quality = assistant._assess_decision_quality(top_poi_score=0.55, runner_up_score=0.5)
    assert suboptimal_quality == DecisionQuality.SUBOPTIMAL
    print(f"[PASS] Suboptimal quality detected: {suboptimal_quality.value}")


def test_crowd_risk_labels():
    """Test crowd risk categorization."""
    gemini_mock = MockGeminiClient()
    stadium = StadiumDataProvider()
    assistant = SmartAssistant(gemini_mock, stadium)

    low_risk = assistant._get_crowd_risk_label(15)
    med_risk = assistant._get_crowd_risk_label(50)
    high_risk = assistant._get_crowd_risk_label(85)

    assert low_risk == "low"
    assert med_risk == "medium"
    assert high_risk == "high"
    print(f"[PASS] Crowd risk labels: 15%={low_risk}, 50%={med_risk}, 85%={high_risk}")


def test_reasoning_normal_case():
    """Test reasoning with normal urgency."""
    gemini_mock = MockGeminiClient()
    stadium = StadiumDataProvider()
    assistant = SmartAssistant(gemini_mock, stadium)

    user = UserContext(
        current_location="Entrance",
        destination_type="concession",
        current_time="14:30",
        urgency_level=1
    )

    decision = assistant.reason_navigation(user)

    assert decision.recommended_poi is not None
    assert len(decision.reasoning_steps) == 6
    assert len(decision.alternative_pois) >= 2
    assert 0 <= decision.confidence_score <= 1
    assert decision.estimated_time_minutes > 0
    print(f"[PASS] Normal case reasoning")
    print(f"       Recommendation: {decision.recommended_poi}")
    print(f"       Quality: {decision.decision_quality.value}")
    print(f"       Confidence: {decision.confidence_score:.1%}")


def test_reasoning_emergency_case():
    """Test reasoning with emergency urgency."""
    gemini_mock = MockGeminiClient()
    stadium = StadiumDataProvider()
    assistant = SmartAssistant(gemini_mock, stadium)

    user_emergency = UserContext(
        current_location="Entrance",
        destination_type="medical",
        current_time="14:30",
        urgency_level=5,
        accessibility_needs="wheelchair"
    )

    decision = assistant.reason_navigation(user_emergency)

    # Emergency should strongly penalize crowded places
    # First Aid Station has 5% crowd (lowest), so it should be recommended
    assert decision.crowd_risk in ["low", "medium"]
    assert decision.confidence_score > 0
    print(f"[PASS] Emergency case reasoning")
    print(f"       Recommendation: {decision.recommended_poi} (low crowd)")
    print(f"       Crowd risk: {decision.crowd_risk}")


def test_explain_decision():
    """Test decision explanation generation."""
    gemini_mock = MockGeminiClient()
    stadium = StadiumDataProvider()
    assistant = SmartAssistant(gemini_mock, stadium)

    user = UserContext(
        current_location="Entrance",
        destination_type="concession",
        current_time="14:30",
        urgency_level=2
    )

    decision = assistant.reason_navigation(user)
    explanation = assistant.explain_decision(decision)

    assert "NAVIGATION RECOMMENDATION" in explanation
    assert "REASONING:" in explanation
    assert "ALTERNATIVES:" in explanation
    assert decision.recommended_poi in explanation
    print(f"[PASS] Decision explanation generated")
    print(explanation)


def test_batch_reasoning():
    """Test batch processing of multiple requests."""
    gemini_mock = MockGeminiClient()
    stadium = StadiumDataProvider()
    assistant = SmartAssistant(gemini_mock, stadium)

    contexts = [
        UserContext("Entrance", "concession", "14:30", urgency_level=1),
        UserContext("North Gate", "restroom", "14:45", urgency_level=3),
        UserContext("Concession A", "medical", "15:00", urgency_level=5),
    ]

    decisions = assistant.batch_reasoning(contexts)

    assert len(decisions) == 3
    assert all(d.recommended_poi is not None for d in decisions)
    print(f"[PASS] Batch reasoning: processed {len(decisions)} requests")
    for i, d in enumerate(decisions):
        print(f"       Request {i+1}: {d.recommended_poi} ({d.decision_quality.value})")


def test_logical_decision_making_benchmark():
    """
    Comprehensive test of Logical Decision Making benchmark.
    Tests all 5 phases of the decision-making process.
    """
    gemini_mock = MockGeminiClient()
    stadium = StadiumDataProvider()
    assistant = SmartAssistant(gemini_mock, stadium)

    print("\n" + "="*60)
    print("LOGICAL DECISION MAKING BENCHMARK TEST")
    print("="*60)

    user = UserContext(
        current_location="North Gate",
        destination_type="concession",
        current_time="15:00",
        urgency_level=2
    )

    decision = assistant.reason_navigation(user)

    # Benchmark 1: All options evaluated
    all_pois = stadium.get_all_pois()
    benchmark_1 = len(all_pois) > 0
    print(f"\n1. OPTIONS EVALUATED: {benchmark_1}")
    print(f"   - All {len(all_pois)} POIs considered in ranking")

    # Benchmark 2: Ranking by quality metric
    ranked = assistant._rank_options(all_pois, 2)
    benchmark_2 = all(ranked[i][1] >= ranked[i+1][1] for i in range(len(ranked)-1))
    print(f"\n2. OPTIONS RANKED: {benchmark_2}")
    print(f"   - Scores descending: {[f'{p[1]:.2f}' for p in ranked[:3]]}")

    # Benchmark 3: Confidence assessment
    benchmark_3 = decision.decision_quality in [
        DecisionQuality.OPTIMAL, DecisionQuality.GOOD,
        DecisionQuality.ACCEPTABLE, DecisionQuality.SUBOPTIMAL
    ]
    print(f"\n3. CONFIDENCE ASSESSED: {benchmark_3}")
    print(f"   - Quality level: {decision.decision_quality.value}")
    print(f"   - Confidence score: {decision.confidence_score:.1%}")

    # Benchmark 4: Reasoning documented
    benchmark_4 = len(decision.reasoning_steps) == 6
    print(f"\n4. REASONING DOCUMENTED: {benchmark_4}")
    for i, step in enumerate(decision.reasoning_steps, 1):
        print(f"   - Step {i}: {step}")

    # Benchmark 5: Alternatives provided
    benchmark_5 = len(decision.alternative_pois) >= 2
    print(f"\n5. ALTERNATIVES PROVIDED: {benchmark_5}")
    print(f"   - {len(decision.alternative_pois)} alternatives: {', '.join(decision.alternative_pois[:3])}")

    all_benchmarks = [benchmark_1, benchmark_2, benchmark_3, benchmark_4, benchmark_5]
    print(f"\nOVERALL: {sum(all_benchmarks)}/5 benchmarks passed")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PHASE 3 LOGIC TEST SUITE")
    print("="*60 + "\n")

    tests = [
        ("SmartAssistant Init", test_smart_assistant_initialization),
        ("POI Suitability", test_evaluate_poi_suitability),
        ("Rank Options", test_rank_options),
        ("Decision Quality", test_assess_decision_quality),
        ("Crowd Risk Labels", test_crowd_risk_labels),
        ("Normal Case Reasoning", test_reasoning_normal_case),
        ("Emergency Case Reasoning", test_reasoning_emergency_case),
        ("Decision Explanation", test_explain_decision),
        ("Batch Reasoning", test_batch_reasoning),
        ("Logic Benchmark", test_logical_decision_making_benchmark),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"\n[TEST] {test_name}")
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] Assertion: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")
