"""
Configuration settings for AI Health Diagnostics Assistant
"""
import os
from pathlib import Path

# Application Settings
APP_NAME = "AI Health Diagnostics Assistant"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Advanced AI-powered blood report analysis system"

# File Upload Settings
MAX_FILE_SIZE_MB = 10
ALLOWED_FILE_TYPES = ['pdf', 'png', 'jpg', 'jpeg']
TEMP_FILE_PREFIX = "temp_"

# AI Model Settings
DEFAULT_MODEL = "llama-3.3-70b-versatile"
SUMMARY_TEMPERATURE = 0.3
CHAT_TEMPERATURE = 0.5
MAX_CHAT_HISTORY = 6

# Vector Store Settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_DIMENSION = 384
FAISS_INDEX_DIR = "faiss_index"
KNOWLEDGE_BASE_DIR = "data/knowledge_base"

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_PATH = DATA_DIR / "knowledge_base"
SAMPLE_REPORTS_PATH = DATA_DIR / "sample_reports"
LOGS_DIR = BASE_DIR / "logs"
USERS_FILE = BASE_DIR / "users.json"

# Create necessary directories
for directory in [DATA_DIR, KNOWLEDGE_BASE_PATH, SAMPLE_REPORTS_PATH, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Medical Parameters Configuration
BLOOD_PARAMETERS = {
    'hemoglobin': {
        'names': ['hemoglobin', 'hb', 'hgb'],
        'unit': 'g/dl',
        'reference': {'male': (13.5, 17.5), 'female': (12.0, 15.5)}
    },
    'hba1c': {
        'names': ['hba1c', 'glycated hemoglobin'],
        'unit': '%',
        'reference': {'male': (4.0, 5.6), 'female': (4.0, 5.6)}
    },
    'glucose': {
        'names': ['glucose', 'blood sugar', 'fasting glucose'],
        'unit': 'mg/dl',
        'reference': {'male': (70, 100), 'female': (70, 100)}
    },
    'cholesterol': {
        'names': ['total cholesterol', 'cholesterol'],
        'unit': 'mg/dl',
        'reference': {'male': (0, 200), 'female': (0, 200)}
    },
    'ldl': {
        'names': ['ldl', 'ldl cholesterol'],
        'unit': 'mg/dl',
        'reference': {'male': (0, 100), 'female': (0, 100)}
    },
    'hdl': {
        'names': ['hdl', 'hdl cholesterol'],
        'unit': 'mg/dl',
        'reference': {'male': (40, 60), 'female': (50, 60)}
    },
    'triglycerides': {
        'names': ['triglycerides', 'tg'],
        'unit': 'mg/dl',
        'reference': {'male': (0, 150), 'female': (0, 150)}
    }
}

# Risk Assessment Thresholds
RISK_LEVELS = {
    'minimal': (0, 5),
    'low': (5, 8),
    'moderate': (8, 15),
    'high': (15, 20),
    'critical': (20, 100)
}

# Security Settings
MIN_USERNAME_LENGTH = 3
MIN_PASSWORD_LENGTH = 6
PASSWORD_HASH_ALGORITHM = 'sha256'
SESSION_TIMEOUT_MINUTES = 60

# UI Settings
PAGE_ICON = "🏥"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# Color Scheme
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#28a745',
    'danger': '#dc3545',
    'warning': '#ffc107',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Rate Limiting
API_RATE_LIMIT_CALLS = 10
API_RATE_LIMIT_WINDOW = 60  # seconds

# Feature Flags
ENABLE_OCR = True
ENABLE_PATIENT_INFO_EXTRACTION = True
ENABLE_REPORT_DOWNLOAD = True
ENABLE_CHAT_HISTORY = True
ENABLE_LOGGING = True

# Disclaimer Text
DISCLAIMER = """
**IMPORTANT DISCLAIMER**: This application is for educational and informational 
purposes only. It is NOT a substitute for professional medical advice, diagnosis, 
or treatment. Always seek the advice of your physician or other qualified health 
provider with any questions you may have regarding a medical condition.
"""

def get_env_variable(var_name: str, default=None):
    """Get environment variable with optional default"""
    return os.getenv(var_name, default)

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check API key
    api_key = get_env_variable('GROQ_API_KEY')
    if not api_key:
        errors.append("GROQ_API_KEY not set in environment")
    
    # Check directories exist
    for directory in [DATA_DIR, KNOWLEDGE_BASE_PATH, LOGS_DIR]:
        if not directory.exists():
            errors.append(f"Directory does not exist: {directory}")
    
    return errors

if __name__ == "__main__":
    # Validate configuration when run directly
    errors = validate_config()
    if errors:
        print("Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration is valid!")
        print(f"App: {APP_NAME} v{APP_VERSION}")
        print(f"Model: {DEFAULT_MODEL}")
