import logging
import os
from pathlib import Path
from datetime import datetime

# Configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_logger(name: str = "app") -> logging.Logger:
    """Setup application logger"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # File handler
        log_file = LOG_DIR / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

def validate_api_key(api_key: str) -> bool:
    """Validate Groq API key format"""
    if not api_key:
        return False
    
    api_key = api_key.strip()
    
    # Check if it's a placeholder
    placeholders = ['your_groq', 'your_api', 'placeholder', 'example']
    if any(ph in api_key.lower() for ph in placeholders):
        return False
    
    # Check basic format (should start with gsk_)
    if not api_key.startswith('gsk_'):
        return False
    
    # Check length (typical Groq keys are ~50 chars)
    if len(api_key) < 30:
        return False
    
    return True

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove path separators and keep only filename
    return Path(filename).name

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def cleanup_temp_files(pattern: str = "temp_*"):
    """Clean up temporary files"""
    import glob
    for temp_file in glob.glob(pattern):
        try:
            os.remove(temp_file)
        except Exception as e:
            print(f"Could not delete {temp_file}: {e}")

class RateLimiter:
    """Simple rate limiter for API calls"""
    def __init__(self, max_calls: int = 10, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_make_call(self) -> bool:
        """Check if a call can be made within rate limit"""
        now = datetime.now()
        
        # Remove old calls outside time window
        self.calls = [call_time for call_time in self.calls
                      if (now - call_time).total_seconds() < self.time_window]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        
        return False
    
    def get_wait_time(self) -> int:
        """Get wait time in seconds before next call"""
        if not self.calls:
            return 0
        
        oldest_call = min(self.calls)
        wait_time = self.time_window - (datetime.now() - oldest_call).total_seconds()
        return max(0, int(wait_time))
