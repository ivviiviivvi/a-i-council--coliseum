"""
NLP Processing Module

Provides natural language processing capabilities for AI agents.
"""

import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from openai import AsyncOpenAI


class NLPProcessor:
    """
    Natural Language Processing module for agent text understanding
    and generation.
    """
    
    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        
        Returns:
            Dict with sentiment label and score
        """
        # Placeholder for actual sentiment analysis
        return {
            "sentiment": "neutral",
            "score": 0.5,
            "confidence": 0.8
        }
    
    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text
        
        Returns:
            List of entities with type and text
        """
        # Placeholder for actual entity extraction
        return []
    
    async def summarize(self, text: str, max_length: int = 100) -> str:
        """
        Summarize text to specified length using an NLP model.
        Falls back to simple slicing if API is unavailable or fails.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized text
        """
        if not self.client:
            return self._fallback_summarize(text, max_length)

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": f"Summarize the following text in {max_length} characters or less."},
                    {"role": "user", "content": text}
                ],
                max_tokens=max_length,
                temperature=0.5
            )
            summary = response.choices[0].message.content.strip()

            if len(summary) > max_length:
                # If the model didn't respect the length constraint, truncate it
                return summary[:max_length] + "..."

            return summary

        except Exception:
            # Fallback on any error (network, auth, rate limit)
            return self._fallback_summarize(text, max_length)

    def _fallback_summarize(self, text: str, max_length: int) -> str:
        """Fallback method for simple string slicing."""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    async def classify_topic(self, text: str) -> Dict[str, float]:
        """
        Classify text into topic categories
        
        Returns:
            Dict of topics with confidence scores
        """
        # Placeholder for topic classification
        return {
            "general": 0.7,
            "politics": 0.2,
            "technology": 0.1
        }
    
    async def extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """
        Extract key terms from text
        
        Args:
            text: Input text
            top_k: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        # Placeholder for keyword extraction
        words = text.lower().split()
        return list(set(words[:top_k]))
