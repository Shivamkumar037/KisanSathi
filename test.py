"""
KrishiVani - API Test Script
Run: python test.py
"""

import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

print("=" * 50)
print("  KrishiVani API Tester")
print("=" * 50)

# --- 1. Keys Check ---
print("\n[1] .env Keys Check:")
print(f"  GROQ_API_KEY  : {'YES (' + GROQ_API_KEY[:8] + '...)' if GROQ_API_KEY and GROQ_API_KEY != 'your_groq_api_key_here' else 'NOT SET'}")
print(f"  GEMINI_API_KEY: {'YES (' + GEMINI_API_KEY[:8] + '...)' if GEMINI_API_KEY and GEMINI_API_KEY != 'your_gemini_api_key_here' else 'NOT SET'}")

# --- 2. Groq Chat Test ---
print("\n[2] Groq Chat Test (llama-3.3-70b):")
if not GROQ_API_KEY or GROQ_API_KEY == 'your_groq_api_key_here':
    print("  SKIP - GROQ_API_KEY nahi mila.")
else:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Tomato ki bimari ke baare mein ek line mein batao."}],
            max_tokens=100
        )
        print("  OK - Groq Chat kaam kar raha hai!")
        print(f"  Response: {response.choices[0].message.content[:120]}")
    except Exception as e:
        print(f"  ERROR - {e}")

# --- 3. Groq Whisper Test ---
print("\n[3] Groq Whisper (Voice) Test:")
if not GROQ_API_KEY or GROQ_API_KEY == 'your_groq_api_key_here':
    print("  SKIP - GROQ_API_KEY nahi mila.")
else:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        models = client.models.list()
        whisper_ok = any('whisper' in m.id for m in models.data)
        print("  OK - Groq Whisper available hai!" if whisper_ok else "  WARN - Whisper model nahi mila")
    except Exception as e:
        print(f"  ERROR - {e}")

# --- 4. Gemini Test ---
print("\n[4] Gemini Vision Test (gemini-2.0-flash):")
if not GEMINI_API_KEY or GEMINI_API_KEY == 'your_gemini_api_key_here':
    print("  SKIP - GEMINI_API_KEY nahi mila.")
else:
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Tomato plant disease ke baare mein ek line mein batao."
        )
        print("  OK - Gemini kaam kar raha hai!")
        print(f"  Response: {response.text[:120]}")
    except Exception as e:
        print(f"  ERROR - {e}")

print("\n" + "=" * 50)
print("  Sab OK hai to: python run.py")
print("  Groq key   : https://console.groq.com")
print("  Gemini key : https://aistudio.google.com")
print("=" * 50)
