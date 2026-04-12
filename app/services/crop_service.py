"""
Crop Service - Business logic for crop disease analysis
Wraps AI service with additional processing, validation, and response formatting
"""

import os
from app.services.ai_service import analyze_crop_image as ai_analyze


def analyze_crop_image(image_path: str) -> dict:
    """
    Full pipeline for crop image analysis:
    1. Validate image file exists
    2. Call AI service for analysis
    3. Post-process and enrich response
    4. Return structured result
    """

    # Step 1: Validate file exists
    if not os.path.exists(image_path):
        return {
            'is_crop_image': False,
            'crop_name': None,
            'disease_detected': None,
            'severity': 'unknown',
            'diagnosis': 'Image file not found. Please try uploading again.',
            'treatment': None,
            'prevention': None,
            'raw_response': 'File not found error'
        }

    # Step 2: Validate file size (max 16MB)
    file_size = os.path.getsize(image_path)
    if file_size > 16 * 1024 * 1024:
        return {
            'is_crop_image': False,
            'crop_name': None,
            'disease_detected': None,
            'severity': 'unknown',
            'diagnosis': 'Image size too large. Please upload image smaller than 16MB.',
            'treatment': None,
            'prevention': None,
            'raw_response': 'File size exceeded'
        }

    # Step 3: Call AI analysis
    result = ai_analyze(image_path)

    # Step 4: Post-process result
    result = _enrich_result(result)

    return result


def _enrich_result(result: dict) -> dict:
    """
    Enrich AI result with additional metadata and fallbacks.
    """

    # If not a crop image, return early with Hindi message
    if not result.get('is_crop_image', True):
        return {
            'is_crop_image': False,
            'crop_name': None,
            'disease_detected': None,
            'severity': 'unknown',
            'diagnosis': result.get(
                'message',
                'पहचान नहीं हो सका। कृपया फसल की स्पष्ट फोटो अपलोड करें।'
            ),
            'treatment': 'कृपया फसल (टमाटर, गेहूं, धान, मिर्च आदि) की फोटो अपलोड करें।',
            'prevention': None,
            'raw_response': result.get('raw_response', '')
        }

    # Normalize severity
    severity = result.get('severity', 'unknown').lower()
    if severity not in ('none', 'low', 'medium', 'high'):
        severity = 'unknown'
    result['severity'] = severity

    # Add severity label in Hindi
    severity_labels = {
        'none': 'कोई रोग नहीं ✅',
        'low': 'हल्का रोग 🟡',
        'medium': 'मध्यम रोग 🟠',
        'high': 'गंभीर रोग 🔴',
        'unknown': 'अज्ञात'
    }
    result['severity_label'] = severity_labels.get(severity, 'अज्ञात')

    # Add urgency label in Hindi
    urgency = result.get('urgency', 'routine')
    urgency_labels = {
        'immediate': '⚠️ तुरंत उपचार करें!',
        'soon': '⏰ जल्द उपचार करें',
        'routine': '✅ सामान्य देखभाल करें'
    }
    result['urgency_label'] = urgency_labels.get(urgency, '✅ सामान्य देखभाल करें')

    # Ensure all expected keys exist with fallbacks
    result.setdefault('crop_name', 'Unknown')
    result.setdefault('crop_name_hindi', '')
    result.setdefault('disease_detected', 'Unknown')
    result.setdefault('disease_hindi', '')
    result.setdefault('diagnosis', 'विश्लेषण उपलब्ध नहीं है।')
    result.setdefault('treatment', 'कृपया नजदीकी कृषि केंद्र से संपर्क करें।')
    result.setdefault('prevention', 'फसल की नियमित निगरानी करें।')
    result.setdefault('recommended_medicines', [])
    result.setdefault('organic_alternatives', [])
    result.setdefault('urgency', 'routine')

    # Add is_healthy flag for easy frontend check
    disease = result.get('disease_detected', '').lower()
    result['is_healthy'] = (
        severity == 'none' or
        'healthy' in disease or
        'स्वस्थ' in disease or
        'theek' in disease
    )

    return result


def get_disease_info(crop_name: str, disease_name: str) -> dict:
    """
    Get static disease info from the known diseases database.
    Useful as fallback when AI is unavailable.
    """
    disease_db = {
        ('tomato', 'leaf spot'): {
            'treatment': '1. रोगग्रस्त पत्तियाँ हटाएं\n2. Mancozeb 75% WP @ 2.5 ग्राम/लीटर पानी में छिड़काव करें\n3. 7 दिन बाद दोबारा छिड़काव करें',
            'prevention': '1. रोगमुक्त बीज उपयोग करें\n2. खेत में पानी जमा न होने दें\n3. फसल चक्र अपनाएं',
            'medicines': ['Mancozeb 75% WP', 'Chlorothalonil']
        },
        ('tomato', 'early blight'): {
            'treatment': '1. Iprodione @ 1.5 ग्राम/लीटर छिड़काव\n2. रोगी पौधों को अलग करें\n3. 10 दिन बाद दोहराएं',
            'prevention': '1. उचित दूरी पर रोपण\n2. ड्रिप सिंचाई उपयोग करें',
            'medicines': ['Iprodione', 'Copper Oxychloride']
        },
        ('wheat', 'rust'): {
            'treatment': '1. Propiconazole 25% EC @ 1 मिली/लीटर छिड़काव\n2. रोगग्रस्त भाग नष्ट करें',
            'prevention': '1. प्रतिरोधी किस्म लगाएं\n2. समय पर बुवाई करें',
            'medicines': ['Propiconazole', 'Tebuconazole']
        },
        ('chili', 'aphid'): {
            'treatment': '1. Imidacloprid 17.8% SL @ 0.5 मिली/लीटर\n2. पीले चिपचिपे ट्रैप लगाएं',
            'prevention': '1. नीम का तेल 5 मिली/लीटर\n2. लेडीबग जैसे प्राकृतिक शत्रु बढ़ाएं',
            'medicines': ['Imidacloprid', 'Thiamethoxam']
        },
        ('sugarcane', 'yellowing'): {
            'treatment': '1. Imidacloprid 2 मिली/लीटर\n2. नाइट्रोजन उर्वरक डालें',
            'prevention': '1. नियमित निगरानी\n2. रोगमुक्त बीज उपयोग करें',
            'medicines': ['Imidacloprid']
        },
    }

    key = (crop_name.lower(), disease_name.lower())
    return disease_db.get(key, {})
