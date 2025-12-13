import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.ai_agents.nlp_module import NLPProcessor

@pytest.mark.asyncio
async def test_extract_entities_success():
    with patch('backend.ai_agents.nlp_module.AsyncOpenAI') as MockClient:
        # Setup mock
        mock_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='{"entities": [{"text": "Elon Musk", "type": "PERSON"}, {"text": "Tesla", "type": "ORG"}]}'))
        ]
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)

        # Instantiate NLPProcessor
        with patch('os.getenv', return_value="fake-key"):
            nlp = NLPProcessor()
            entities = await nlp.extract_entities("Elon Musk announced a new Tesla model.")

            assert len(entities) == 2
            assert entities[0]['text'] == "Elon Musk"
            assert entities[0]['type'] == "PERSON"
            assert entities[1]['text'] == "Tesla"
            assert entities[1]['type'] == "ORG"

@pytest.mark.asyncio
async def test_extract_entities_no_key():
    with patch('os.getenv', return_value=None):
        nlp = NLPProcessor()
        entities = await nlp.extract_entities("Elon Musk announced a new Tesla model.")
        assert entities == []

@pytest.mark.asyncio
async def test_extract_entities_api_error():
    with patch('backend.ai_agents.nlp_module.AsyncOpenAI') as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))

        with patch('os.getenv', return_value="fake-key"):
            nlp = NLPProcessor()
            entities = await nlp.extract_entities("Elon Musk announced a new Tesla model.")
            assert entities == []
