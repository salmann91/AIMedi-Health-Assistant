"""
Test suite for AI Health Diagnostics Assistant
Run with: python test_system.py
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    errors = []
    
    try:
        import streamlit
        print("✓ Streamlit")
    except ImportError as e:
        errors.append(f"✗ Streamlit: {e}")
    
    try:
        from langchain_groq import ChatGroq
        print("✓ LangChain Groq")
    except ImportError as e:
        errors.append(f"✗ LangChain Groq: {e}")
    
    try:
        import pdfplumber
        print("✓ PDFPlumber")
    except ImportError as e:
        errors.append(f"✗ PDFPlumber: {e}")
    
    try:
        import faiss
        print("✓ FAISS")
    except ImportError as e:
        errors.append(f"✗ FAISS: {e}")
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✓ Sentence Transformers")
    except ImportError as e:
        errors.append(f"✗ Sentence Transformers: {e}")
    
    try:
        import plotly
        print("✓ Plotly")
    except ImportError as e:
        errors.append(f"✗ Plotly: {e}")
    
    try:
        from reportlab.lib.pagesizes import letter
        print("✓ ReportLab")
    except ImportError as e:
        errors.append(f"✗ ReportLab: {e}")
    
    return errors

def test_directories():
    """Test if required directories exist"""
    print("\nTesting directories...")
    errors = []
    
    required_dirs = [
        'data',
        'data/knowledge_base',
        'faiss_index',
        'logs',
        'report_processing',
        'ai',
        'analytics',
        'rag',
        'dashboard'
    ]
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path}")
        else:
            errors.append(f"✗ {dir_path} not found")
            print(f"✗ {dir_path}")
    
    return errors

def test_files():
    """Test if required files exist"""
    print("\nTesting files...")
    errors = []
    
    required_files = [
        'app.py',
        'auth.py',
        'config.py',
        'utils.py',
        'requirements.txt',
        '.env',
        'README.md'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            errors.append(f"✗ {file_path} not found")
            print(f"✗ {file_path}")
    
    return errors

def test_env_variables():
    """Test environment variables"""
    print("\nTesting environment variables...")
    errors = []
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        if api_key.startswith('gsk_'):
            print(f"✓ GROQ_API_KEY is set (length: {len(api_key)})")
        else:
            errors.append("✗ GROQ_API_KEY doesn't start with 'gsk_'")
    else:
        errors.append("✗ GROQ_API_KEY not set")
    
    return errors

def test_auth_system():
    """Test authentication system"""
    print("\nTesting authentication system...")
    errors = []
    
    try:
        from auth import hash_password, verify_user, create_default_admin
        
        # Test password hashing
        test_pass = "test123"
        hashed = hash_password(test_pass)
        if len(hashed) == 64:  # SHA-256 produces 64 char hex
            print("✓ Password hashing works")
        else:
            errors.append("✗ Password hashing incorrect")
        
        # Test default admin creation
        create_default_admin()
        if verify_user("admin", "admin123"):
            print("✓ Default admin user created")
        else:
            errors.append("✗ Default admin verification failed")
        
    except Exception as e:
        errors.append(f"✗ Auth system error: {e}")
    
    return errors

def test_modules():
    """Test custom modules"""
    print("\nTesting custom modules...")
    errors = []
    
    modules = [
        ('report_processing.extractor', 'BloodReportExtractor'),
        ('report_processing.parser', 'ReportParser'),
        ('analytics.analyzer', 'HealthAnalyzer'),
        ('analytics.risk_engine', 'RiskEngine'),
        ('ai.summary_generator', 'SummaryGenerator'),
        ('ai.chatbot', 'HealthChatbot'),
        ('rag.vector_store', 'VectorStore'),
        ('dashboard.charts', 'DashboardCharts')
    ]
    
    for module_path, class_name in modules:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✓ {module_path}.{class_name}")
        except Exception as e:
            errors.append(f"✗ {module_path}.{class_name}: {e}")
            print(f"✗ {module_path}.{class_name}")
    
    return errors

def main():
    """Run all tests"""
    print("="*60)
    print("AI Health Diagnostics Assistant - System Test")
    print("="*60)
    
    all_errors = []
    
    all_errors.extend(test_imports())
    all_errors.extend(test_directories())
    all_errors.extend(test_files())
    all_errors.extend(test_env_variables())
    all_errors.extend(test_auth_system())
    all_errors.extend(test_modules())
    
    print("\n" + "="*60)
    if all_errors:
        print(f"❌ Tests completed with {len(all_errors)} errors:")
        for error in all_errors:
            print(f"  {error}")
        print("\nPlease fix the errors above before running the application.")
        return 1
    else:
        print("✅ All tests passed! System is ready.")
        print("\nTo start the application, run:")
        print("  streamlit run app.py")
        return 0

if __name__ == "__main__":
    sys.exit(main())
