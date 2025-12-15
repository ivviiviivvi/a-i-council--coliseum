"""
NLP Processing Module

Provides natural language processing capabilities for AI agents.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from pydantic import BaseModel

# Set up logging
logger = logging.getLogger(__name__)

class NLPProcessor:
    """
    Natural Language Processing module for agent text understanding
    and generation.
    """
    
    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("OPENAI_API_KEY not found. NLP capabilities will be limited.")
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        
        Returns:
            Dict with sentiment label and score
        """
        if self.client:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a sentiment analysis assistant. "
                                "Analyze the sentiment of the following text. "
                                "Return a JSON object with keys: 'sentiment' (one of 'positive', 'negative', 'neutral'), "
                                "'score' (float between -1.0 and 1.0), and 'confidence' (float between 0.0 and 1.0). "
                                "Do not include markdown formatting or code blocks."
                            )
                        },
                        {"role": "user", "content": text}
                    ],
                    temperature=0.0
                )

                content = response.choices[0].message.content
                # Strip code block markers if present, just in case
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]

                result = json.loads(content.strip())
                return result

            except Exception as e:
                logger.error(f"Error calling OpenAI for sentiment analysis: {e}")
                # Fallback to dummy data

        # Fallback for missing API key or errors
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
        Summarize text to specified length
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized text
        """
        # Placeholder for actual summarization
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
