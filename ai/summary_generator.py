import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from .prompts import SUMMARY_PROMPT, RECOMMENDATION_PROMPT
from typing import Dict
import json

class SummaryGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        try:
            self.llm = ChatGroq(
                groq_api_key=self.api_key,
                model_name="llama-3.3-70b-versatile",
                temperature=0.3
            )
        except Exception as e:
            print(f"Error initializing summary generator: {e}")
            raise
    
    def generate_summary(self, analysis_results: Dict) -> str:
        """Generate AI summary from analysis results"""
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
            return "Error generating summary. Please check your test results manually."
    
    def generate_recommendations(self, abnormalities: list) -> str:
        """Generate personalized recommendations"""
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
