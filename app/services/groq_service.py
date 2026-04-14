import requests
from app.config import Config

def get_groq_response(prompt: str, system_prompt: str = None) -> str:
    """Groq se response - Updated with working model"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": "llama-3.1-8b-instant",     # ← Yeh ab working model hai (fast + free)
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print("Groq Error:", response.status_code, response.text[:300])
            return "Maaf kijiye, abhi Groq se baat nahi ho pa rahi hai. Thodi der baad try kijiye."
        
        return response.json()["choices"][0]["message"]["content"].strip()
        
    except Exception as e:
        print("Groq Exception:", str(e))
        return "Maaf kijiye, abhi AI se baat nahi ho pa rahi hai. Kripya thodi der baad try kijiye."