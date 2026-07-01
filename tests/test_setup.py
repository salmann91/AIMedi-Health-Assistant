"""
Test script to verify the setup and Groq API connection
"""
import os
from dotenv import load_dotenv

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        import streamlit
        import langchain
        import langchain_groq
        import pdfplumber
        import faiss
        import sentence_transformers
        import plotly
        import pandas
        import numpy
        print("✅ All required packages are installed correctly!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_env_file():
    """Test if .env file is configured"""
    print("\nTesting .env configuration...")
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env file")
        return False
    elif api_key == 'your_groq_api_key_here':
        print("⚠️ Please update GROQ_API_KEY in .env file with your actual API key")
        return False
    else:
        print("✅ GROQ_API_KEY is configured")
        return True

def test_groq_connection():
    """Test Groq API connection"""
    print("\nTesting Groq API connection...")
    try:
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY')
        
        if not api_key or api_key == 'your_groq_api_key_here':
            print("⚠️ Skipping API test - Please configure your API key first")
            return False
        
        from langchain_groq import ChatGroq
        from langchain.schema import HumanMessage
        
        llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.3
        )
        
        response = llm.invoke([HumanMessage(content="Say 'Connection successful!' in one sentence.")])
        print(f"✅ Groq API connection successful! Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Groq API connection failed: {e}")
        return False

def test_folder_structure():
    """Test if all required folders exist"""
    print("\nTesting folder structure...")
    required_folders = [
        'data',
        'data/sample_reports',
        'data/knowledge_base',
        'report_processing',
        'analytics',
        'rag',
        'ai',
        'dashboard',
        'tests',
        'docs'
    ]
    
    all_exist = True
    for folder in required_folders:
        if os.path.exists(folder):
            print(f"✅ {folder}")
        else:
            print(f"❌ {folder} - Missing")
            all_exist = False
    
    return all_exist

def test_knowledge_base():
    """Test if knowledge base files exist"""
    print("\nTesting knowledge base files...")
    kb_files = [
        'data/knowledge_base/hemoglobin.txt',
        'data/knowledge_base/hba1c.txt',
        'data/knowledge_base/cholesterol.txt',
        'data/knowledge_base/kidney.txt',
        'data/knowledge_base/liver.txt',
        'data/knowledge_base/thyroid.txt'
    ]
    
    all_exist = True
    for file in kb_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing")
            all_exist = False
    
    return all_exist

def main():
    print("="*60)
    print("AI Health Diagnostics Assistant - Setup Verification")
    print("="*60)
    
    results = {
        'Imports': test_imports(),
        'Environment': test_env_file(),
        'Folder Structure': test_folder_structure(),
        'Knowledge Base': test_knowledge_base(),
        'Groq Connection': test_groq_connection()
    }
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print("\n")
    
    if all(results.values()):
        print("🎉 All tests passed! Your setup is complete.")
        print("\nNext steps:")
        print("1. Run the application: streamlit run app.py")
        print("2. Upload a blood report PDF")
        print("3. Analyze and chat with the AI assistant")
    else:
        print("⚠️ Some tests failed. Please fix the issues above before running the application.")
        if not results['Environment']:
            print("\n📝 Don't forget to add your Groq API key to the .env file!")
            print("   Get your key from: https://console.groq.com/keys")

if __name__ == "__main__":
    main()
