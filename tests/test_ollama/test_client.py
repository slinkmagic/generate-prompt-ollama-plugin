"""Tests for Ollama API client module."""

import json
import pytest
import responses
from unittest.mock import Mock, patch

from src.ollama.client import OllamaClient, OllamaAPIError, OllamaClientPool
from src.ollama.config import OllamaConfig


class TestOllamaClient:
    """Test OllamaClient class."""
    
    def setup_method(self):
        """Setup test method."""
        self.config = OllamaConfig(
            endpoint="http://localhost:11434",
            model="test-model",
            timeout=30,
            max_retries=3
        )
        self.client = OllamaClient(self.config)
        
    def teardown_method(self):
        """Teardown test method."""
        self.client.close()
        
    def test_init_with_config(self):
        """Test initialization with custom config."""
        assert self.client.config == self.config
        assert self.client.session is not None
        
    def test_init_without_config(self):
        """Test initialization without config."""
        with patch('src.ollama.client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.ollama = self.config
            mock_get_config.return_value = mock_config
            
            client = OllamaClient()
            assert client.config == self.config
            client.close()
            
    def test_build_prompt_template(self):
        """Test prompt template building."""
        original = "a beautiful landscape"
        template = self.client._build_prompt_template(original)
        
        assert "a beautiful landscape" in template
        assert "Enhanced prompt:" in template
        assert "Maximum 50 tokens" in template
        
    def test_parse_response_json(self):
        """Test parsing JSON response."""
        response_text = '{"response": "enhanced prompt text"}'
        result = self.client._parse_response(response_text)
        assert result == "enhanced prompt text"
        
    def test_parse_response_plain_text(self):
        """Test parsing plain text response."""
        response_text = "Enhanced prompt: beautiful sunset scene"
        result = self.client._parse_response(response_text)
        assert result == "beautiful sunset scene"
        
    def test_parse_response_multiline(self):
        """Test parsing multiline response."""
        response_text = """
        # Comment line
        Enhanced prompt: scenic mountain view
        // Another comment
        """
        result = self.client._parse_response(response_text)
        assert result == "scenic mountain view"
        
    @responses.activate
    def test_enhance_prompt_success(self):
        """Test successful prompt enhancement."""
        # Mock API response
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json={"response": "with vibrant colors and dramatic lighting"},
            status=200
        )
        
        original = "a beautiful landscape"
        result = self.client.enhance_prompt(original)
        
        assert original in result
        assert "vibrant colors" in result
        assert "dramatic lighting" in result
        
    @responses.activate
    def test_enhance_prompt_api_error(self):
        """Test prompt enhancement with API error."""
        # Mock API error response
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json={"error": "Model not found"},
            status=404
        )
        
        with pytest.raises(OllamaAPIError):
            self.client.enhance_prompt("test prompt")
            
    @responses.activate
    def test_enhance_prompt_timeout(self):
        """Test prompt enhancement timeout."""
        # Mock timeout by not adding any response
        with pytest.raises(OllamaAPIError):
            self.client.enhance_prompt("test prompt")
            
    @responses.activate
    def test_enhance_prompts_batch(self):
        """Test batch prompt enhancement."""
        # Mock API responses
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json={"response": "enhanced1"},
            status=200
        )
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json={"response": "enhanced2"},
            status=200
        )
        
        prompts = ["prompt1", "prompt2"]
        results = self.client.enhance_prompts_batch(prompts)
        
        assert len(results) == 2
        assert "prompt1" in results[0]
        assert "enhanced1" in results[0]
        assert "prompt2" in results[1]
        assert "enhanced2" in results[1]
        
    @responses.activate
    def test_enhance_prompts_batch_with_failure(self):
        """Test batch enhancement with one failure."""
        # Mock one success and one failure
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json={"response": "enhanced1"},
            status=200
        )
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json={"error": "Server error"},
            status=500
        )
        
        prompts = ["prompt1", "prompt2"]
        results = self.client.enhance_prompts_batch(prompts)
        
        assert len(results) == 2
        assert "enhanced1" in results[0]
        assert results[1] == "prompt2"  # Original prompt as fallback
        
    @responses.activate
    def test_test_connection_success(self):
        """Test successful connection test."""
        # Mock API response
        responses.add(
            responses.GET,
            "http://localhost:11434/api/tags",
            json={
                "models": [
                    {"name": "test-model"},
                    {"name": "other-model"}
                ]
            },
            status=200
        )
        
        result = self.client.test_connection()
        assert result is True
        
    @responses.activate
    def test_test_connection_failure(self):
        """Test failed connection test."""
        # Mock API error
        responses.add(
            responses.GET,
            "http://localhost:11434/api/tags",
            json={"error": "Connection failed"},
            status=500
        )
        
        result = self.client.test_connection()
        assert result is False
        
    def test_close(self):
        """Test client close."""
        self.client.close()
        # Should not raise exception


class TestOllamaClientPool:
    """Test OllamaClientPool class."""
    
    def setup_method(self):
        """Setup test method."""
        self.pool = OllamaClientPool(pool_size=2)
        
    def teardown_method(self):
        """Teardown test method."""
        self.pool.close()
        
    def test_init(self):
        """Test pool initialization."""
        assert len(self.pool.clients) == 2
        assert all(isinstance(client, OllamaClient) for client in self.pool.clients)
        
    @pytest.mark.asyncio
    async def test_enhance_prompts_concurrent(self):
        """Test concurrent prompt enhancement."""
        # Mock the enhance_prompt method
        for client in self.pool.clients:
            client.enhance_prompt = Mock(side_effect=lambda p: f"enhanced {p}")
            
        prompts = ["prompt1", "prompt2", "prompt3"]
        results = await self.pool.enhance_prompts_concurrent(prompts)
        
        assert len(results) == 3
        assert all("enhanced" in result for result in results)
        
    @pytest.mark.asyncio
    async def test_enhance_prompts_concurrent_empty(self):
        """Test concurrent enhancement with empty list."""
        results = await self.pool.enhance_prompts_concurrent([])
        assert results == []
        
    @pytest.mark.asyncio
    async def test_enhance_prompts_concurrent_with_failure(self):
        """Test concurrent enhancement with failure."""
        # Mock one client to fail
        self.pool.clients[0].enhance_prompt = Mock(side_effect=Exception("API Error"))
        self.pool.clients[1].enhance_prompt = Mock(side_effect=lambda p: f"enhanced {p}")
        
        prompts = ["prompt1", "prompt2"]
        results = await self.pool.enhance_prompts_concurrent(prompts)
        
        assert len(results) == 2
        assert results[0] == "prompt1"  # Original prompt as fallback
        assert "enhanced prompt2" in results[1]
        
    def test_close(self):
        """Test pool close."""
        self.pool.close()
        # Should not raise exception