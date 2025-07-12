"""Ollama API configuration management module."""

import json
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, HttpUrl, Field, field_validator


class OllamaConfig(BaseModel):
    """Ollama API configuration model."""
    
    endpoint: HttpUrl = Field(default="http://localhost:11434", description="Ollama API endpoint")
    model: str = Field(default="openhermes", description="Model name to use")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    max_retries: int = Field(default=5, ge=1, le=10, description="Maximum retry attempts")
    
    @field_validator('model')
    @classmethod
    def validate_model(cls, v):
        """Validate model name."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Model name cannot be empty")
        return v.strip()
    

class PromptConfig(BaseModel):
    """Prompt expansion configuration model."""
    
    max_tokens: int = Field(default=150, ge=50, le=500, description="Maximum tokens for expanded prompt")
    template_language: str = Field(default="en", description="Template language")
    template_max_tokens: int = Field(default=50, ge=10, le=100, description="Maximum tokens for template")
    expansion_targets: list[str] = Field(
        default=[
            "scene", "background", "mood", "color_tone", 
            "composition", "camera_angle", "lighting", "theme", "concept"
        ],
        description="Prompt expansion target categories"
    )
    expansion_excludes: list[str] = Field(
        default=["artist_name", "technique", "style_info"],
        description="Prompt expansion exclude categories"
    )
    

class UIConfig(BaseModel):
    """UI configuration model."""
    
    show_progress: bool = Field(default=True, description="Show progress bar")
    show_status: bool = Field(default=True, description="Show status text")
    show_preview: bool = Field(default=False, description="Show preview")
    

class LoggingConfig(BaseModel):
    """Logging configuration model."""
    
    level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    format: str = Field(default="json", pattern="^(json|text)$")
    include_timestamp: bool = Field(default=True, description="Include timestamp in logs")
    log_api_communication: bool = Field(default=True, description="Log API communication details")
    log_prompt_conversion: bool = Field(default=True, description="Log prompt conversion details")
    

class PerformanceConfig(BaseModel):
    """Performance configuration model."""
    
    memory_limit_gb: float = Field(default=1.0, ge=0.1, le=16.0, description="Memory limit in GB")
    cpu_limit_percent: int = Field(default=50, ge=10, le=100, description="CPU limit percentage")
    

class Config(BaseModel):
    """Main configuration model."""
    
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    prompt: PromptConfig = Field(default_factory=PromptConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    

class ConfigManager:
    """Configuration manager for loading and saving config."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize config manager.
        
        Args:
            config_path: Path to config file. Defaults to config/default_config.json
        """
        if config_path is None:
            self.config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config", "default_config.json"
            )
        else:
            self.config_path = config_path
            
        self._config: Optional[Config] = None
        
    def load_config(self) -> Config:
        """Load configuration from file.
        
        Returns:
            Config: Loaded configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                self._config = Config(**config_data)
            else:
                # Create default config
                self._config = Config()
                self.save_config()
                
            return self._config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading config: {e}")
            
    def save_config(self) -> None:
        """Save current configuration to file.
        
        Raises:
            ValueError: If no config is loaded
        """
        if self._config is None:
            raise ValueError("No config loaded to save")
            
        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config.model_dump(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Error saving config: {e}")
            
    def get_config(self) -> Config:
        """Get current configuration.
        
        Returns:
            Config: Current configuration
        """
        if self._config is None:
            return self.load_config()
        return self._config
        
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values.
        
        Args:
            updates: Dictionary of configuration updates
            
        Raises:
            ValueError: If updates are invalid
        """
        if self._config is None:
            self.load_config()
            
        try:
            # Create updated config data
            current_data = self._config.model_dump()
            
            # Deep update nested dictionaries
            def deep_update(base_dict, update_dict):
                for key, value in update_dict.items():
                    if isinstance(value, dict) and key in base_dict:
                        deep_update(base_dict[key], value)
                    else:
                        base_dict[key] = value
                        
            deep_update(current_data, updates)
            
            # Validate updated config
            self._config = Config(**current_data)
            
        except Exception as e:
            raise ValueError(f"Error updating config: {e}")


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get global config manager instance.
    
    Returns:
        ConfigManager: Global config manager
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> Config:
    """Get current configuration.
    
    Returns:
        Config: Current configuration
    """
    return get_config_manager().get_config()