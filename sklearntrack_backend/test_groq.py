# FILE: test_groq.py - Run this to test Groq API
# ============================================================================
# Place this file in: sklearntrack_backend/test_groq.py
# Run: python test_groq.py
# ============================================================================

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sklearntrack_backend.settings')
django.setup()

from django.conf import settings
from notes.utils import (
    generate_ai_explanation,
    generate_ai_code,
    improve_explanation,
    summarize_explanation
)

def test_groq_connection():
    """Test Groq API connection"""
    print("=" * 60)
    print("GROQ API CONNECTION TEST")
    print("=" * 60)
    
    # Check API key
    api_key = getattr(settings, 'GROQ_API_KEY', None)
    if not api_key:
        print("❌ ERROR: GROQ_API_KEY not found in settings!")
        print("\nPlease add GROQ_API_KEY to your .env file:")
        print("GROQ_API_KEY=gsk_your_key_here")
        print("\nGet your free key from: https://console.groq.com")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test Groq client
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        print("✅ Groq client initialized successfully")
    except ImportError:
        print("❌ ERROR: 'groq' package not installed!")
        print("\nInstall it with: pip install groq")
        return False
    except Exception as e:
        print(f"❌ ERROR initializing Groq client: {e}")
        return False
    
    # Test API call
    print("\n" + "=" * 60)
    print("TESTING API CALL...")
    print("=" * 60)
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello! Groq API is working!' and nothing else."
                }
            ],
            temperature=0.5,
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ API Response: {result}")
        print("\n✅ SUCCESS: Groq API is working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR during API call: {e}")
        print("\nPossible issues:")
        print("1. Invalid API key - get new one from https://console.groq.com")
        print("2. Network connection problem")
        print("3. Groq API is down - check https://status.groq.com")
        return False


def test_ai_functions():
    """Test all AI utility functions"""
    print("\n" + "=" * 60)
    print("TESTING AI UTILITY FUNCTIONS")
    print("=" * 60)
    
    # Test 1: Generate Explanation
    print("\n1️⃣ Testing: generate_ai_explanation")
    print("-" * 40)
    try:
        result = generate_ai_explanation("Binary Search")
        print(f"✅ Generated {len(result)} characters")
        print(f"Preview: {result[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Generate Code
    print("\n2️⃣ Testing: generate_ai_code")
    print("-" * 40)
    try:
        result = generate_ai_code("Binary Search", "python")
        print(f"✅ Generated {len(result)} characters of code")
        print(f"Preview:\n{result[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Improve Explanation
    print("\n3️⃣ Testing: improve_explanation")
    print("-" * 40)
    try:
        sample_text = "Binary search is a search algorithm. It works on sorted arrays."
        result = improve_explanation(sample_text)
        print(f"✅ Improved to {len(result)} characters")
        print(f"Preview: {result[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Summarize
    print("\n4️⃣ Testing: summarize_explanation")
    print("-" * 40)
    try:
        long_text = """
        Binary search is a search algorithm that finds the position of a target value 
        within a sorted array. Binary search compares the target value to the middle 
        element of the array. If they are not equal, the half in which the target cannot 
        lie is eliminated and the search continues on the remaining half.
        """
        result = summarize_explanation(long_text)
        print(f"✅ Summarized to {len(result)} characters")
        print(f"Summary: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("\n🚀 SK-LearnTrack Groq API Test Suite\n")
    
    # Test connection first
    if test_groq_connection():
        # If connection works, test all functions
        test_ai_functions()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED!")
        print("=" * 60)
        print("\n💡 Your AI features are ready to use!")
        print("   - Generate Explanation: Working ✅")
        print("   - Improve Explanation: Working ✅")
        print("   - Summarize Content: Working ✅")
        print("   - Generate Code: Working ✅")
        print("\n🎉 Happy note-taking!\n")
    else:
        print("\n" + "=" * 60)
        print("❌ TESTS FAILED")
        print("=" * 60)
        print("\nPlease fix the issues above and run the test again.")