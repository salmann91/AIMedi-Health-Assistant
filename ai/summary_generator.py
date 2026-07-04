import os
import json
from typing import Dict

try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import SystemMessage, HumanMessage
except Exception:  # pragma: no cover - defensive import fallback
    ChatGroq = None
    SystemMessage = HumanMessage = None

from .prompts import SUMMARY_PROMPT, RECOMMENDATION_PROMPT


class SummaryGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.llm = None

        if not self.api_key or ChatGroq is None or SystemMessage is None or HumanMessage is None:
            self._available = False
            return

        try:
            self.llm = ChatGroq(
                groq_api_key=self.api_key,
                model_name="llama-3.3-70b-versatile",
                temperature=0.3
            )
            self._available = True
        except Exception as e:
            print(f"Error initializing summary generator: {e}")
            self._available = False

    def generate_summary(self, analysis_results: Dict) -> str:
        """Generate AI summary from analysis results or return a safe fallback."""
        if not self._available or self.llm is None:
            return "Unable to generate AI summary. The AI service is not available right now. Please review the analysis manually."

        try:
            results_str = json.dumps(analysis_results.get('results', []), indent=2)
            risk_str = json.dumps(analysis_results.get('risk_assessment', {}), indent=2)

            prompt = SUMMARY_PROMPT.format(
                results=results_str,
                risk_assessment=risk_str
            )

            messages = [
                SystemMessage(content="You are a medical AI assistant providing blood test analysis."),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Unable to generate AI summary. Please check your test results manually."

    def generate_recommendations(self, abnormalities: list) -> str:
        """Generate personalized recommendations or return a safe fallback."""
        if not self._available or self.llm is None:
            return "The AI recommendation service is unavailable. Please consult a healthcare professional for advice."

        try:
            abnormalities_str = json.dumps(abnormalities, indent=2)

            prompt = RECOMMENDATION_PROMPT.format(
                abnormalities=abnormalities_str
            )

            messages = [
                SystemMessage(content="You are a medical AI assistant providing health recommendations."),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return "Error generating recommendations. Please consult with a healthcare professional."
