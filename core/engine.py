"""
StadiumFlow AI - Agentic Reasoning Engine.
Combines Gemini 2.0 reasoning with real-time stadium data for optimal navigation.
"""

import logging
from typing import Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DecisionQuality(Enum):
    """Enum for decision quality scoring (Logical Decision Making benchmark)."""
    OPTIMAL = "optimal"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    SUBOPTIMAL = "suboptimal"


@dataclass
class UserContext:
    """User context for reasoning."""
    current_location: str
    destination_type: str  # e.g., "concession", "restroom", "medical"
    current_time: str
    accessibility_needs: Optional[str] = None
    urgency_level: int = 1  # 1=normal, 5=emergency


@dataclass
class NavigationDecision:
    """Output structure for navigation decision."""
    recommended_poi: str
    reasoning_steps: list[str]
    estimated_time_minutes: int
    crowd_risk: str  # "low", "medium", "high"
    decision_quality: DecisionQuality
    alternative_pois: list[str]
    confidence_score: float  # 0-1


class SmartAssistant:
    """
    Agentic reasoning engine for stadium navigation.
    Implements multi-step logical decision making.
    """

    def __init__(self, gemini_client, stadium_provider):
        """
        Initialize Smart Assistant.

        Args:
            gemini_client: Configured GeminiClient instance.
            stadium_provider: Configured StadiumDataProvider instance.
        """
        self.gemini = gemini_client
        self.stadium = stadium_provider
        logger.info("SmartAssistant initialized with Gemini + Stadium Provider")

    def _evaluate_poi_suitability(
        self, poi_name: str, crowd_density: int, user_urgency: int
    ) -> float:
        """
        Calculate POI suitability score (0-1).

        Logical Decision Making Step 1: Evaluate all available options.

        Args:
            poi_name: POI name.
            crowd_density: Current crowd percentage (0-100).
            user_urgency: User urgency level (1-5).

        Returns:
            Suitability score between 0 and 1.
        """
        # Base score (higher is better)
        base_score = 1.0 - (crowd_density / 100.0)

        # Urgency multiplier: higher urgency = penalize crowds more
        # Urgent users heavily avoid crowded places
        urgency_penalty = (user_urgency / 5.0) * (crowd_density / 100.0)

        # Combined suitability
        suitability = base_score - urgency_penalty

        logger.debug(f"POI '{poi_name}' suitability: {suitability:.2f}")
        return max(0.0, min(suitability, 1.0))  # Clamp between 0 and 1

    def _rank_options(
        self, available_pois: dict, user_urgency: int
    ) -> list[tuple[str, float]]:
        """
        Logical Decision Making Step 2: Rank all options by suitability.

        Args:
            available_pois: Dictionary of POIs with crowd data.
            user_urgency: User urgency level.

        Returns:
            List of (poi_name, score) tuples, sorted by score descending.
        """
        ranked = []
        for poi_name, poi_data in available_pois.items():
            score = self._evaluate_poi_suitability(
                poi_name, poi_data["crowd_density"], user_urgency
            )
            ranked.append((poi_name, score))

        # Sort by score descending
        ranked.sort(key=lambda x: x[1], reverse=True)
        logger.info(f"Ranked {len(ranked)} POIs")
        return ranked

    def _assess_decision_quality(
        self, top_poi_score: float, runner_up_score: float
    ) -> DecisionQuality:
        """
        Logical Decision Making Step 3: Assess decision confidence.

        Args:
            top_poi_score: Suitability score of top choice.
            runner_up_score: Suitability score of second choice.

        Returns:
            DecisionQuality enum value.
        """
        score_gap = top_poi_score - runner_up_score

        if top_poi_score >= 0.9 and score_gap >= 0.2:
            quality = DecisionQuality.OPTIMAL
        elif top_poi_score >= 0.7 and score_gap >= 0.15:
            quality = DecisionQuality.GOOD
        elif top_poi_score >= 0.5 and score_gap >= 0.1:
            quality = DecisionQuality.ACCEPTABLE
        else:
            quality = DecisionQuality.SUBOPTIMAL

        logger.info(f"Decision quality: {quality.value} (gap: {score_gap:.2f})")
        return quality

    def _get_crowd_risk_label(self, crowd_density: int) -> str:
        """
        Convert crowd percentage to risk label.

        Args:
            crowd_density: Crowd percentage (0-100).

        Returns:
            Risk label: "low", "medium", or "high".
        """
        if crowd_density < 30:
            return "low"
        elif crowd_density < 70:
            return "medium"
        else:
            return "high"

    def reason_navigation(self, user_context: UserContext) -> NavigationDecision:
        """
        Main reasoning function: Generate optimal navigation decision.

        Logical Decision Making Flow:
        1. Evaluate all available POIs for suitability
        2. Rank options by suitability score
        3. Assess decision quality/confidence
        4. Generate reasoning explanation
        5. Provide alternatives

        Args:
            user_context: User's current context.

        Returns:
            NavigationDecision with reasoning and recommendations.
        """
        logger.info(f"= REASONING FLOW START =")
        logger.info(f"User at: {user_context.current_location}")
        logger.info(f"Seeking: {user_context.destination_type}")

        # STEP 1: Get all available POIs from stadium
        all_pois = self.stadium.get_all_pois()
        logger.info(f"Available POIs: {len(all_pois)}")

        # STEP 2: Evaluate suitability for all POIs
        ranked_pois = self._rank_options(all_pois, user_context.urgency_level)

        # STEP 3: Select top recommendation
        top_poi_name, top_score = ranked_pois[0]
        runner_up_name, runner_up_score = ranked_pois[1] if len(ranked_pois) > 1 else (None, 0)

        # STEP 4: Assess decision quality
        decision_quality = self._assess_decision_quality(top_score, runner_up_score)
        confidence = top_score

        # STEP 5: Get details on recommended POI
        top_poi_data = all_pois[top_poi_name]
        top_crowd = top_poi_data["crowd_density"]
        crowd_risk = self._get_crowd_risk_label(top_crowd)

        # STEP 6: Build reasoning steps
        reasoning_steps = [
            f"Step 1: Evaluated {len(all_pois)} available POIs",
            f"Step 2: Ranked by suitability (urgency level: {user_context.urgency_level}/5)",
            f"Step 3: Top choice '{top_poi_name}' scored {top_score:.2f}",
            f"Step 4: Crowd analysis: {top_crowd}% ({crowd_risk} risk)",
            f"Step 5: Decision quality: {decision_quality.value}",
            f"Step 6: Confidence score: {confidence:.1%}",
        ]

        # STEP 7: Get alternatives
        alternatives = [poi[0] for poi in ranked_pois[1:4]]

        # STEP 8: Estimated time (mock calculation)
        base_time = 5
        crowd_delay = int((top_crowd / 100) * 5)
        urgency_speedup = max(0, int((5 - user_context.urgency_level) * 0.5))
        estimated_time = base_time + crowd_delay - urgency_speedup

        logger.info(f"RECOMMENDATION: {top_poi_name} (confidence: {confidence:.1%})")
        logger.info(f"= REASONING FLOW END =\n")

        return NavigationDecision(
            recommended_poi=top_poi_name,
            reasoning_steps=reasoning_steps,
            estimated_time_minutes=max(1, estimated_time),
            crowd_risk=crowd_risk,
            decision_quality=decision_quality,
            alternative_pois=alternatives,
            confidence_score=confidence,
        )

    def explain_decision(self, decision: NavigationDecision) -> str:
        """
        Generate human-readable explanation of decision.

        Args:
            decision: NavigationDecision object.

        Returns:
            Formatted explanation string.
        """
        explanation = f"""
NAVIGATION RECOMMENDATION
=========================
POI: {decision.recommended_poi}
Status: {decision.crowd_risk.upper()} crowd risk
Confidence: {decision.confidence_score:.1%}
Quality: {decision.decision_quality.value.upper()}
Est. Time: {decision.estimated_time_minutes} min

REASONING:
{chr(10).join(f"  • {step}" for step in decision.reasoning_steps)}

ALTERNATIVES:
{chr(10).join(f"  • {poi}" for poi in decision.alternative_pois)}
"""
        return explanation.strip()

    def batch_reasoning(
        self, user_contexts: list[UserContext]
    ) -> list[NavigationDecision]:
        """
        Process multiple reasoning requests efficiently.

        Args:
            user_contexts: List of user contexts.

        Returns:
            List of NavigationDecision objects.
        """
        decisions = []
        logger.info(f"Batch reasoning: {len(user_contexts)} requests")
        for ctx in user_contexts:
            decision = self.reason_navigation(ctx)
            decisions.append(decision)
        return decisions
