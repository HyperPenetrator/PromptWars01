"""
Gemini 2.0 Client for StadiumFlow AI.
Handles reasoning about stadium navigation and crowd density analysis.
"""

import os
import logging
from typing import Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiClient:
    """Robust client for Google Gemini 2.0 API with error handling."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize Gemini client.

        Args:
            api_key: Google Gemini API key. If None, reads from GEMINI_API_KEY env var.

        Raises:
            ValueError: If API key is not provided or found in environment.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not provided. Set it in .env or pass as argument."
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        logger.info("✓ Gemini 2.0 client initialized successfully")

    def analyze_crowd_density(
        self, location: str, crowd_level: int, poi_list: list[str]
    ) -> str:
        """
        Analyze crowd density and recommend fastest path to POI.

        Args:
            location: Current user location.
            crowd_level: Crowd density (0-100 scale).
            poi_list: List of points of interest.

        Returns:
            Reasoning string with path recommendation.
        """
        prompt = f"""
        You are a smart stadium navigation assistant.
        User is at location: {location}
        Current crowd density: {crowd_level}%
        Available Points of Interest (POIs): {', '.join(poi_list)}

        Based on the crowd density, provide the fastest logical path to reach a POI.
        Format: "Recommended POI: [name] | Reasoning: [explanation] | Estimated Time: [time]"
        Be concise but clear.
        """
        try:
            response = self.model.generate_content(prompt)
            logger.info(f"✓ Analysis generated for {location}")
            return response.text
        except Exception as e:
            logger.error(f"✗ Gemini API error: {str(e)}")
            return f"Error: Unable to generate analysis. {str(e)}"

    def reasoning_chain(
        self, user_query: str, context_data: dict
    ) -> str:
        """
        Multi-step reasoning chain for complex queries.

        Args:
            user_query: User's question or request.
            context_data: Additional context (crowd data, event info, etc).

        Returns:
            Detailed reasoning response.
        """
        prompt = f"""
        Context: {context_data}
        User Query: {user_query}

        Provide step-by-step reasoning:
        1. Analyze the situation
        2. Identify constraints
        3. Recommend action
        """
        try:
            response = self.model.generate_content(prompt)
            logger.info("✓ Reasoning chain completed")
            return response.text
        except Exception as e:
            logger.error(f"✗ Reasoning chain error: {str(e)}")
            return f"Error in reasoning chain: {str(e)}"

    def health_check(self) -> bool:
        """
        Verify Gemini API connection.

        Returns:
            True if API is reachable, False otherwise.
        """
        try:
            test_prompt = "Say 'Connected' only."
            response = self.model.generate_content(test_prompt)
            if response.text:
                logger.info("✓ Gemini API health check passed")
                return True
        except Exception as e:
            logger.error(f"✗ Health check failed: {str(e)}")
        return False
