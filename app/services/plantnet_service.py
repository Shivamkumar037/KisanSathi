import requests
from app.config import Config

def analyze_crop_image(image_path: str) -> dict:
    """PlantNet - Fixed version (length mismatch error solved)"""
    url = f"https://my-api.plantnet.org/v2/identify/all?api-key={Config.PLANTNET_API_KEY}"
    
    try:
        with open(image_path, 'rb') as img:
            files = {'images': img}
            # PlantNet ko exactly same length chahiye images aur organs ka
            data = {'organs': ['leaf']}   # single image ke liye single organ

            response = requests.post(url, files=files, data=data, timeout=25)
            
            if response.status_code != 200:
                print("PlantNet Error:", response.status_code, response.text)
                return {
    "success": False,
    "message": "⚠️ फसल की पहचान नहीं हो पाई। कृपया Community में जाकर अपनी फोटो शेयर करें और विशेषज्ञों से सलाह लें।"
}
            
            result = response.json()
            
            if result.get('results') and len(result['results']) > 0:
                best = result['results'][0]
                return {
                    "success": True,
                    "plant": best['species']['commonNames'][0] if best['species'].get('commonNames') else best['species']['scientificName'],
                    "confidence": round(best['score'] * 100, 2)
                }
            
            return {"success": False, "message": "Koi crop clearly nahi dikha raha image mein."}
            
    except Exception as e:
        print("PlantNet Exception:", str(e))
        return {"success": False, "message": f"Analysis fail ho gaya: {str(e)}"}