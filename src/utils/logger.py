"""Logging utility module."""

import json
import logging
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

from ..ollama.config import get_config


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            str: JSON formatted log entry
        """
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage'):
                log_entry[key] = value
                
        return json.dumps(log_entry, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Text formatter for human-readable logging."""
    
    def __init__(self):
        """Initialize text formatter."""
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


class APILoggerAdapter(logging.LoggerAdapter):
    """Logger adapter for API communication logging."""
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Process log message with API context.
        
        Args:
            msg: Log message
            kwargs: Keyword arguments
            
        Returns:
            tuple: Processed message and kwargs
        """
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra
        return msg, kwargs
        
    def log_api_request(self, url: str, method: str, payload: Dict[str, Any]):
        """Log API request details.
        
        Args:
            url: Request URL
            method: HTTP method
            payload: Request payload
        """
        self.info(
            f"API Request: {method} {url}",
            extra={
                "api_request": {
                    "url": url,
                    "method": method,
                    "payload": payload,
                    "timestamp": time.time()
                }
            }
        )
        
    def log_api_response(self, url: str, status_code: int, response_data: Any, elapsed_time: float):
        """Log API response details.
        
        Args:
            url: Request URL
            status_code: HTTP status code
            response_data: Response data
            elapsed_time: Request elapsed time
        """
        self.info(
            f"API Response: {status_code} from {url} ({elapsed_time:.2f}s)",
            extra={
                "api_response": {
                    "url": url,
                    "status_code": status_code,
                    "response_data": response_data,
                    "elapsed_time": elapsed_time,
                    "timestamp": time.time()
                }
            }
        )
        
    def log_prompt_conversion(self, original: str, enhanced: str):
        """Log prompt conversion details.
        
        Args:
            original: Original prompt
            enhanced: Enhanced prompt
        """
        self.info(
            "Prompt conversion completed",
            extra={
                "prompt_conversion": {
                    "original": original,
                    "enhanced": enhanced,
                    "original_length": len(original),
                    "enhanced_length": len(enhanced),
                    "timestamp": time.time()
                }
            }
        )


class LoggerManager:
    """Logger manager for the plugin."""
    
    def __init__(self):
        """Initialize logger manager."""
        self._loggers: Dict[str, logging.Logger] = {}
        self._setup_done = False
        
    def setup_logging(self):
        """Setup logging configuration."""
        if self._setup_done:
            return
            
        try:
            config = get_config().logging
            
            # Set up root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(getattr(logging, config.level))
            
            # Clear existing handlers
            root_logger.handlers.clear()
            
            # Create console handler
            console_handler = logging.StreamHandler(sys.stdout)
            
            # Set formatter based on config
            if config.format == "json":
                formatter = JSONFormatter()
            else:
                formatter = TextFormatter()
                
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
            
            # Create file handler if log file is specified
            if hasattr(config, 'log_file') and config.log_file:
                log_file = Path(config.log_file)
                log_file.parent.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
                
            self._setup_done = True
            
        except Exception as e:
            # Fallback to basic logging if config fails
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler(sys.stdout)]
            )
            logging.error(f"Failed to setup logging from config: {e}")
            
    def get_logger(self, name: str) -> logging.Logger:
        """Get logger by name.
        
        Args:
            name: Logger name
            
        Returns:
            logging.Logger: Logger instance
        """
        if not self._setup_done:
            self.setup_logging()
            
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
            
        return self._loggers[name]
        
    def get_api_logger(self, name: str) -> APILoggerAdapter:
        """Get API logger adapter.
        
        Args:
            name: Logger name
            
        Returns:
            APILoggerAdapter: API logger adapter
        """
        logger = self.get_logger(name)
        return APILoggerAdapter(logger, {"component": "api"})


# Global logger manager
_logger_manager: Optional[LoggerManager] = None


def get_logger_manager() -> LoggerManager:
    """Get global logger manager.
    
    Returns:
        LoggerManager: Global logger manager
    """
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager


def get_logger(name: str) -> logging.Logger:
    """Get logger by name.
    
    Args:
        name: Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    return get_logger_manager().get_logger(name)


def get_api_logger(name: str) -> APILoggerAdapter:
    """Get API logger adapter.
    
    Args:
        name: Logger name
        
    Returns:
        APILoggerAdapter: API logger adapter
    """
    return get_logger_manager().get_api_logger(name)