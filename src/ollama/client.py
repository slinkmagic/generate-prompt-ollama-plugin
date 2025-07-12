"""Ollama API client module for prompt enhancement."""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import get_config, OllamaConfig
from ..utils.logger import get_logger


class OllamaAPIError(Exception):
    """Custom exception for Ollama API errors."""
    pass


class OllamaClient:
    """Ollama API client for prompt enhancement."""
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        """Initialize Ollama client.
        
        Args:
            config: Ollama configuration. If None, uses global config.
        """
        if config is None:
            self.config = get_config().ollama
        else:
            self.config = config
            
        self.logger = get_logger(__name__)
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry strategy.
        
        Returns:
            requests.Session: Configured session
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "generate-prompt-ollama-plugin/1.0.0"
        })
        
        return session
        
    def _build_prompt_template(self, original_prompt: str) -> str:
        """Build prompt template for Ollama API.
        
        Args:
            original_prompt: Original user prompt
            
        Returns:
            str: Formatted prompt template
        """
        template = f"""Enhance this image generation prompt by adding complementary details. 
Keep the original meaning and add scene, background, mood, lighting, or composition details.
Do not add artist names, specific techniques, or style information.
Maximum 50 tokens for additions.

Original prompt: {original_prompt}

Enhanced prompt:"""
        
        return template
        
    def _parse_response(self, response_text: str) -> str:
        """Parse Ollama API response to extract enhanced prompt.
        
        Args:
            response_text: Raw response from Ollama API
            
        Returns:
            str: Enhanced prompt text
            
        Raises:
            OllamaAPIError: If response cannot be parsed
        """
        try:
            # Try to parse as JSON first
            if response_text.strip().startswith('{'):
                data = json.loads(response_text)
                if 'response' in data:
                    return data['response'].strip()
                elif 'text' in data:
                    return data['text'].strip()
                    
            # If not JSON, treat as plain text
            lines = response_text.strip().split('\n')
            
            # Look for enhanced prompt in response
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('//'):
                    # Remove common prefixes
                    prefixes = ['Enhanced prompt:', 'Result:', 'Output:', 'Enhanced:']
                    for prefix in prefixes:
                        if line.startswith(prefix):
                            line = line[len(prefix):].strip()
                            break
                    
                    if line:
                        return line
                        
            # If no suitable line found, return the whole response
            return response_text.strip()
            
        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            # Return original text as fallback
            return response_text.strip()
            
    def enhance_prompt(self, original_prompt: str) -> str:
        """Enhance prompt using Ollama API.
        
        Args:
            original_prompt: Original user prompt
            
        Returns:
            str: Enhanced prompt
            
        Raises:
            OllamaAPIError: If API request fails
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Enhancing prompt: {original_prompt[:100]}...")
            
            # Build request payload
            prompt_template = self._build_prompt_template(original_prompt)
            
            payload = {
                "model": self.config.model,
                "prompt": prompt_template,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 150
                }
            }
            
            # Make API request
            api_url = f"{str(self.config.endpoint).rstrip('/')}/api/generate"
            
            self.logger.debug(f"Making request to {api_url}")
            response = self.session.post(
                api_url,
                json=payload,
                timeout=self.config.timeout
            )
            
            # Check response status
            if response.status_code != 200:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                self.logger.error(error_msg)
                raise OllamaAPIError(error_msg)
                
            # Parse response
            response_data = response.json()
            enhanced_text = ""
            
            if 'response' in response_data:
                enhanced_text = self._parse_response(response_data['response'])
            else:
                self.logger.warning(f"Unexpected response format: {response_data}")
                enhanced_text = str(response_data)
                
            # Log successful request
            elapsed_time = time.time() - start_time
            self.logger.info(f"Prompt enhanced successfully in {elapsed_time:.2f}s")
            
            # Combine original and enhanced prompt
            if enhanced_text and enhanced_text.lower() != original_prompt.lower():
                result = f"{original_prompt}, {enhanced_text}"
            else:
                result = original_prompt
                
            self.logger.debug(f"Final enhanced prompt: {result}")
            return result
            
        except requests.exceptions.Timeout:
            error_msg = f"Request timeout after {self.config.timeout}s"
            self.logger.error(error_msg)
            raise OllamaAPIError(error_msg)
            
        except requests.exceptions.ConnectionError:
            error_msg = f"Connection error to {self.config.endpoint}"
            self.logger.error(error_msg)
            raise OllamaAPIError(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error during prompt enhancement: {e}"
            self.logger.error(error_msg)
            raise OllamaAPIError(error_msg)
            
    def enhance_prompts_batch(self, prompts: List[str]) -> List[str]:
        """Enhance multiple prompts with variation.
        
        Args:
            prompts: List of original prompts
            
        Returns:
            List[str]: List of enhanced prompts
        """
        enhanced_prompts = []
        
        for i, prompt in enumerate(prompts):
            try:
                self.logger.info(f"Enhancing prompt {i+1}/{len(prompts)}")
                enhanced = self.enhance_prompt(prompt)
                enhanced_prompts.append(enhanced)
                
                # Add small delay between requests to avoid overwhelming the API
                if i < len(prompts) - 1:
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Failed to enhance prompt {i+1}: {e}")
                # Use original prompt as fallback
                enhanced_prompts.append(prompt)
                
        return enhanced_prompts
        
    def test_connection(self) -> bool:
        """Test connection to Ollama API.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.info("Testing Ollama API connection...")
            
            # Try to get model info
            api_url = f"{str(self.config.endpoint).rstrip('/')}/api/tags"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                model_names = [model.get('name', '') for model in models]
                
                self.logger.info(f"Connection successful. Available models: {model_names}")
                
                # Check if configured model is available
                if self.config.model in model_names:
                    self.logger.info(f"Configured model '{self.config.model}' is available")
                else:
                    self.logger.warning(f"Configured model '{self.config.model}' not found in available models")
                    
                return True
            else:
                self.logger.error(f"Connection test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
            
    def close(self):
        """Close the HTTP session."""
        if self.session:
            self.session.close()
            

class OllamaClientPool:
    """Pool of Ollama clients for concurrent processing."""
    
    def __init__(self, pool_size: int = 3):
        """Initialize client pool.
        
        Args:
            pool_size: Number of clients in pool
        """
        self.pool_size = pool_size
        self.clients: List[OllamaClient] = []
        self.logger = get_logger(__name__)
        
        # Initialize clients
        for _ in range(pool_size):
            self.clients.append(OllamaClient())
            
    async def enhance_prompts_concurrent(self, prompts: List[str]) -> List[str]:
        """Enhance prompts concurrently using client pool.
        
        Args:
            prompts: List of prompts to enhance
            
        Returns:
            List[str]: Enhanced prompts
        """
        if not prompts:
            return []
            
        enhanced_prompts = [""] * len(prompts)
        
        async def enhance_single(client: OllamaClient, index: int, prompt: str):
            """Enhance single prompt asynchronously."""
            try:
                enhanced = await asyncio.get_event_loop().run_in_executor(
                    None, client.enhance_prompt, prompt
                )
                enhanced_prompts[index] = enhanced
            except Exception as e:
                self.logger.error(f"Failed to enhance prompt {index}: {e}")
                enhanced_prompts[index] = prompt
                
        # Create tasks for all prompts
        tasks = []
        for i, prompt in enumerate(prompts):
            client = self.clients[i % len(self.clients)]
            task = enhance_single(client, i, prompt)
            tasks.append(task)
            
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        
        return enhanced_prompts
        
    def close(self):
        """Close all clients in pool."""
        for client in self.clients:
            client.close()