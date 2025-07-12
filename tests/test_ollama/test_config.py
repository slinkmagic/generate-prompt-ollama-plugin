"""Tests for Ollama configuration module."""

import json
import os
import tempfile
import pytest
from unittest.mock import patch

from src.ollama.config import (
    OllamaConfig, PromptConfig, UIConfig, LoggingConfig, 
    PerformanceConfig, Config, ConfigManager
)


class TestOllamaConfig:
    """Test OllamaConfig model."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = OllamaConfig()
        assert str(config.endpoint) == "http://localhost:11434"
        assert config.model == "openhermes"
        assert config.timeout == 30
        assert config.max_retries == 5
        
    def test_valid_config(self):
        """Test valid configuration creation."""
        config = OllamaConfig(
            endpoint="http://example.com:8080",
            model="llama2",
            timeout=60,
            max_retries=3
        )
        assert str(config.endpoint) == "http://example.com:8080/"
        assert config.model == "llama2"
        assert config.timeout == 60
        assert config.max_retries == 3
        
    def test_invalid_model(self):
        """Test invalid model validation."""
        with pytest.raises(ValueError):
            OllamaConfig(model="")
            
        with pytest.raises(ValueError):
            OllamaConfig(model="   ")
            
    def test_invalid_timeout(self):
        """Test invalid timeout validation."""
        with pytest.raises(ValueError):
            OllamaConfig(timeout=0)
            
        with pytest.raises(ValueError):
            OllamaConfig(timeout=301)
            
    def test_invalid_retries(self):
        """Test invalid retries validation."""
        with pytest.raises(ValueError):
            OllamaConfig(max_retries=0)
            
        with pytest.raises(ValueError):
            OllamaConfig(max_retries=11)


class TestPromptConfig:
    """Test PromptConfig model."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = PromptConfig()
        assert config.max_tokens == 150
        assert config.template_language == "en"
        assert config.template_max_tokens == 50
        assert "scene" in config.expansion_targets
        assert "artist_name" in config.expansion_excludes
        
    def test_valid_config(self):
        """Test valid configuration creation."""
        config = PromptConfig(
            max_tokens=200,
            template_language="ja",
            expansion_targets=["mood", "lighting"]
        )
        assert config.max_tokens == 200
        assert config.template_language == "ja"
        assert config.expansion_targets == ["mood", "lighting"]


class TestConfig:
    """Test main Config model."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = Config()
        assert isinstance(config.ollama, OllamaConfig)
        assert isinstance(config.prompt, PromptConfig)
        assert isinstance(config.ui, UIConfig)
        assert isinstance(config.logging, LoggingConfig)
        assert isinstance(config.performance, PerformanceConfig)
        
    def test_nested_config(self):
        """Test nested configuration creation."""
        config = Config(
            ollama={"model": "llama2", "timeout": 45},
            prompt={"max_tokens": 200}
        )
        assert config.ollama.model == "llama2"
        assert config.ollama.timeout == 45
        assert config.prompt.max_tokens == 200


class TestConfigManager:
    """Test ConfigManager class."""
    
    def setup_method(self):
        """Setup test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.json")
        
    def teardown_method(self):
        """Teardown test method."""
        if os.path.exists(self.config_path):
            os.unlink(self.config_path)
        os.rmdir(self.temp_dir)
        
    def test_init_with_custom_path(self):
        """Test initialization with custom config path."""
        manager = ConfigManager(self.config_path)
        assert manager.config_path == self.config_path
        
    def test_load_default_config(self):
        """Test loading default config when file doesn't exist."""
        manager = ConfigManager(self.config_path)
        config = manager.load_config()
        
        assert isinstance(config, Config)
        assert os.path.exists(self.config_path)
        
    def test_load_existing_config(self):
        """Test loading existing config file."""
        # Create test config file
        test_config = {
            "ollama": {
                "endpoint": "http://test:8080",
                "model": "test-model",
                "timeout": 60,
                "max_retries": 3
            },
            "prompt": {
                "max_tokens": 200,
                "template_language": "en",
                "template_max_tokens": 50,
                "expansion_targets": ["scene", "mood"],
                "expansion_excludes": ["artist_name"]
            },
            "ui": {
                "show_progress": True,
                "show_status": True,
                "show_preview": False
            },
            "logging": {
                "level": "DEBUG",
                "format": "json",
                "include_timestamp": True,
                "log_api_communication": True,
                "log_prompt_conversion": True
            },
            "performance": {
                "memory_limit_gb": 2.0,
                "cpu_limit_percent": 80
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
            
        manager = ConfigManager(self.config_path)
        config = manager.load_config()
        
        assert config.ollama.model == "test-model"
        assert config.ollama.timeout == 60
        assert config.prompt.max_tokens == 200
        
    def test_load_invalid_json(self):
        """Test loading invalid JSON file."""
        with open(self.config_path, 'w') as f:
            f.write("invalid json content")
            
        manager = ConfigManager(self.config_path)
        
        with pytest.raises(ValueError):
            manager.load_config()
            
    def test_save_config(self):
        """Test saving configuration."""
        manager = ConfigManager(self.config_path)
        config = manager.load_config()
        
        # Modify config
        config.ollama.model = "new-model"
        manager._config = config
        manager.save_config()
        
        # Load and verify
        with open(self.config_path, 'r') as f:
            saved_data = json.load(f)
            
        assert saved_data["ollama"]["model"] == "new-model"
        
    def test_save_config_no_config_loaded(self):
        """Test saving config when no config is loaded."""
        manager = ConfigManager(self.config_path)
        
        with pytest.raises(ValueError):
            manager.save_config()
            
    def test_get_config(self):
        """Test getting configuration."""
        manager = ConfigManager(self.config_path)
        config = manager.get_config()
        
        assert isinstance(config, Config)
        
    def test_update_config(self):
        """Test updating configuration."""
        manager = ConfigManager(self.config_path)
        manager.load_config()
        
        updates = {
            "ollama": {
                "model": "updated-model",
                "timeout": 90
            },
            "prompt": {
                "max_tokens": 300
            }
        }
        
        manager.update_config(updates)
        config = manager.get_config()
        
        assert config.ollama.model == "updated-model"
        assert config.ollama.timeout == 90
        assert config.prompt.max_tokens == 300
        
    def test_update_config_invalid(self):
        """Test updating config with invalid values."""
        manager = ConfigManager(self.config_path)
        manager.load_config()
        
        updates = {
            "ollama": {
                "timeout": 500  # Invalid: exceeds max
            }
        }
        
        with pytest.raises(ValueError):
            manager.update_config(updates)


def test_global_config_manager():
    """Test global config manager functions."""
    from src.ollama.config import get_config_manager, get_config
    
    manager1 = get_config_manager()
    manager2 = get_config_manager()
    
    # Should return same instance
    assert manager1 is manager2
    
    # Should return valid config
    config = get_config()
    assert isinstance(config, Config)