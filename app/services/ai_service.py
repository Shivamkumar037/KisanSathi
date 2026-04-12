"""
AI Service - FREE APIs (Groq Only)
- Groq llama-3.3-70b    -> Chat
- Groq whisper-large-v3 -> Voice Transcription
- Groq llava-v1.5-7b    -> Crop Image Analysis (Gemini replaced)
- Browser Web Speech API -> TTS (no backend needed)
"""

import os
import json
import base64

_groq_client = None


def get_groq_client():
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return None
        try:
            # httpx version compatibility fix
            import httpx
            import groq._base_client as _bc
            orig_init = httpx.Client.__init__
            def patched_init(self, *args, **kwargs):
                kwargs.pop('proxies', None)
                orig_init(self, *args, **kwargs)
            httpx.Client.__init__ = patched_init
        except Exception:
            pass
        from groq import Groq
        _groq_client = Groq(api_key=api_key)
    return _groq_client


# --- Crop Disease Analysis (Groq llava - FREE) ---

def analyze_crop_image(image_path: str) -> dict:
    client = get_groq_client()
    if not client:
        return _mock_crop_analysis()
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # Detect image extension
        ext = image_path.rsplit('.', 1)[-1].lower() if '.' in image_path else 'jpeg'
        if ext == 'jpg':
            ext = 'jpeg'
        media_type = f'image/{ext}' if ext in ('jpeg', 'png', 'webp', 'gif') else 'image/jpeg'

        prompt = """You are an expert agricultural scientist and crop doctor.
Analyze this crop/plant image carefully.

STEP 1: Determine if this is actually a crop/plant/agricultural image.
- If NOT a crop image, respond ONLY with: {"is_crop_image": false, "message": "पहचान नहीं हो सका। कृपया फसल की फोटो अपलोड करें।"}

STEP 2: If it IS a crop image, respond in this EXACT JSON format:
{
  "is_crop_image": true,
  "crop_name": "crop name in English",
  "crop_name_hindi": "crop name in Hindi",
  "disease_detected": "disease name or Healthy",
  "disease_hindi": "disease name in Hindi",
  "severity": "none/low/medium/high",
  "diagnosis": "2-3 sentences in Hindi",
  "treatment": "Step by step treatment in Hindi numbered list",
  "prevention": "Prevention tips in Hindi numbered list",
  "urgency": "immediate/soon/routine",
  "recommended_medicines": ["medicine1", "medicine2"],
  "organic_alternatives": ["organic1", "organic2"]
}
Respond ONLY with valid JSON, no other text."""

        response = client.chat.completions.create(
            model="llava-v1.5-7b-4096-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1024,
            temperature=0.3
        )

        raw = response.choices[0].message.content.strip()

        # Clean markdown fences if present
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        result['raw_response'] = raw
        return result

    except json.JSONDecodeError:
        return {
            'is_crop_image': True,
            'crop_name': 'Unknown',
            'disease_detected': 'Analysis Error',
            'severity': 'unknown',
            'diagnosis': 'विश्लेषण में समस्या हुई। स्पष्ट फोटो अपलोड करें।',
            'treatment': 'नजदीकी कृषि केंद्र से संपर्क करें।',
            'prevention': 'नियमित निगरानी करें।',
            'raw_response': ''
        }
    except Exception as e:
        print(f"Crop analysis error: {e}")
        return {
            'is_crop_image': True,
            'crop_name': 'Unknown',
            'disease_detected': 'Service Unavailable',
            'severity': 'unknown',
            'diagnosis': f'AI सेवा उपलब्ध नहीं: {str(e)}',
            'treatment': 'बाद में पुनः प्रयास करें।',
            'prevention': 'कृषि केंद्र से संपर्क करें।',
            'raw_response': str(e)
        }


def _mock_crop_analysis() -> dict:
    return {
        'is_crop_image': True,
        'crop_name': 'Demo',
        'crop_name_hindi': 'डेमो',
        'disease_detected': 'No API Key',
        'disease_hindi': 'API Key नहीं है',
        'severity': 'none',
        'diagnosis': 'असली analysis के लिए GROQ_API_KEY set करें।',
        'treatment': '1. console.groq.com पर जाएं\n2. Free API key लें\n3. .env में GROQ_API_KEY set करें',
        'prevention': 'API key set करने के बाद सब काम करेगा।',
        'urgency': 'routine',
        'recommended_medicines': [],
        'organic_alternatives': [],
        'raw_response': 'MOCK'
    }


# --- AI Chat (Groq llama-3.3-70b - FREE) ---

SYSTEM_HI = """आप KrishiVani के AI कृषि सहायक "कृषि मित्र" हैं।
भारतीय किसानों की मदद करें: फसल रोग, कीट नियंत्रण, खाद, सिंचाई, योजनाएं, मंडी भाव।
हमेशा सरल हिंदी में जवाब दें। हर जवाब में एक व्यावहारिक सुझाव दें।"""

SYSTEM_EN = """You are KrishiVani's AI Agricultural Assistant "Krishi Mitra".
Help Indian farmers with crop diseases, pest control, fertilizers, irrigation, government schemes, market rates.
Give practical advice in simple language."""


def get_ai_response(message: str, history: list, language: str = 'hi') -> str:
    client = get_groq_client()
    if not client:
        return _mock_chat_response(message, language)
    try:
        messages = [{"role": "system", "content": SYSTEM_HI if language == 'hi' else SYSTEM_EN}]
        for msg in history[-20:]:
            messages.append({"role": msg['role'], "content": msg['content']})
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=600,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq chat error: {e}")
        return "माफ करें, AI सेवा अभी उपलब्ध नहीं है। कृपया बाद में प्रयास करें।" if language == 'hi' else "AI service temporarily unavailable."


def _mock_chat_response(message: str, language: str) -> str:
    if language == 'hi':
        return 'नमस्ते! 🌱 असली AI जवाब के लिए GROQ_API_KEY set करें।\nconsole.groq.com पर जाएं और free key लें।'
    return 'Hello! Set GROQ_API_KEY for real AI responses. Get free key at console.groq.com 🌱'


# --- Voice Transcription (Groq Whisper - FREE) ---

def transcribe_audio(audio_path: str, language: str = 'hi') -> str:
    client = get_groq_client()
    if not client:
        return "नमस्ते, मेरी फसल में समस्या है।"
    try:
        with open(audio_path, 'rb') as f:
            transcript = client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3",
                language='hi' if language == 'hi' else 'en',
                response_format="text"
            )
        return transcript.strip() if transcript else None
    except Exception as e:
        print(f"Groq transcription error: {e}")
        return None


# --- TTS - Browser Web Speech API (completely free) ---

def text_to_speech(text: str, language: str = 'hi') -> dict:
    return {'success': True, 'path': None, 'use_browser_tts': True, 'text': text}
