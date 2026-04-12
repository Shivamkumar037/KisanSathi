# 🌾 KrishiVani - AI Farmer Assistant Platform

**KrishiVani** is a full-stack web platform for Indian farmers, featuring AI-powered crop disease detection, voice assistance, live mandi prices, government schemes, and a farmer community.

---

## 📱 Features

| Feature | Description |
|---|---|
| 🔍 **Crop Disease AI** | Upload crop photo → AI detects disease, gives treatment in Hindi |
| 🎤 **Voice Chat** | Speak in Hindi/English → AI answers farming questions |
| 💬 **AI Text Chat** | Chat with AI assistant about any farming problem |
| 📊 **Mandi Bhav** | Live market rates for 12+ crops across UP mandis |
| 📋 **Govt Schemes** | PM-Kisan, PMFBY, KCC, PMKSY and more |
| 👥 **Community** | Share crop problems, comment, help other farmers |
| 🌤️ **Weather** | Local weather and 5-day forecast |
| 🔐 **Auth** | Login/Signup with phone number |

---

## 🚀 Quick Setup

### 1. Clone and Install
```bash
cd krishivani
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Initialize Database
```bash
python manage.py init_db
```

### 4. Run the Server
```bash
python run.py
```
Server starts at: **http://localhost:5000**

---

## 🔑 API Keys Required

| Service | Key | Required? | Use |
|---|---|---|---|
| OpenAI | `OPENAI_API_KEY` | **Yes** (for AI features) | Crop analysis, chat, voice |
| OpenWeatherMap | `OPENWEATHERMAP_API_KEY` | Optional | Live weather data |

**Without OpenAI key:** App runs in demo mode with mock AI responses.

---

## 📁 Project Structure

```
krishivani/
├── run.py                      # App entry point
├── manage.py                   # Database management CLI
├── requirements.txt
├── .env.example                # Environment template
│
├── app/
│   ├── __init__.py             # App factory, extension init
│   │
│   ├── models/                 # Database models
│   │   ├── user.py             # User accounts
│   │   ├── crop.py             # Crop scan results
│   │   ├── market.py           # Mandi rates
│   │   ├── scheme.py           # Government schemes
│   │   ├── community.py        # Posts & comments
│   │   └── chat.py             # Chat messages
│   │
│   ├── routes/                 # API endpoints
│   │   ├── auth.py             # Login, signup, profile
│   │   ├── crops.py            # Crop disease detection
│   │   ├── market.py           # Market rates
│   │   ├── schemes.py          # Government schemes
│   │   ├── community.py        # Community feed
│   │   ├── chat.py             # AI chat + WebSocket
│   │   └── weather.py          # Weather data
│   │
│   ├── services/               # Business logic
│   │   ├── ai_service.py       # OpenAI integration
│   │   ├── market_service.py   # Market data seeding
│   │   └── scheme_service.py   # Scheme data seeding
│   │
│   └── utils/
│       ├── file_handler.py     # Image/audio upload utils
│       └── validators.py       # Input validation
│
├── data/
│   └── csv/
│       └── market_rates_sample.csv  # Sample mandi data
│
└── uploads/                    # User uploaded files (auto-created)
    ├── crops/                  # Crop analysis images
    ├── profiles/               # Profile pictures
    ├── community/              # Community post images
    └── audio/                  # Voice messages
```

---

## 📡 API Reference

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register new farmer |
| POST | `/api/auth/login` | Login with phone + password |
| GET | `/api/auth/profile` | Get profile (JWT required) |
| PUT | `/api/auth/profile` | Update profile |
| POST | `/api/auth/profile/image` | Upload profile picture |

### Crop Disease Detection
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/crops/analyze` | Analyze crop image (JWT) |
| POST | `/api/crops/analyze/public` | Analyze without login |
| GET | `/api/crops/history` | User's scan history |
| GET | `/api/crops/<id>` | Get scan result |
| GET | `/api/crops/diseases` | List known diseases |

### Market Rates
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/market/rates` | All rates (filterable) |
| GET | `/api/market/rates/gorakhpur` | Gorakhpur mandi rates |
| GET | `/api/market/mandis` | List all mandis |
| GET | `/api/market/commodity/<name>` | Price history |
| GET | `/api/market/trending` | Price movers today |
| POST | `/api/market/upload-csv` | Bulk import via CSV |

### Government Schemes
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/schemes/` | All schemes |
| GET | `/api/schemes/<id>` | Scheme details |
| GET | `/api/schemes/category/<cat>` | Filter by category |
| GET | `/api/schemes/search?q=` | Search schemes |

### AI Chat
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat/message` | Send text message |
| POST | `/api/chat/voice` | Send voice message |
| GET | `/api/chat/sessions` | Chat history |
| GET | `/api/chat/sessions/<id>` | Session messages |
| DELETE | `/api/chat/sessions/<id>` | Delete session |

### Community
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/community/posts` | Feed |
| POST | `/api/community/posts` | Create post |
| GET | `/api/community/posts/<id>` | Post + comments |
| POST | `/api/community/posts/<id>/like` | Toggle like |
| POST | `/api/community/posts/<id>/comments` | Add comment |
| DELETE | `/api/community/comments/<id>` | Delete comment |

### Weather
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/weather/current?city=Gorakhpur` | Current weather |
| GET | `/api/weather/forecast?city=Gorakhpur` | 5-day forecast |

---

## 🛠️ Management Commands

```bash
python manage.py init_db          # Initialize DB + seed data
python manage.py seed_market      # Re-seed market rates
python manage.py seed_schemes     # Re-seed govt schemes
python manage.py load_csv <file>  # Import CSV market data
python manage.py create_admin     # Create a test user
python manage.py stats            # Show DB statistics
python manage.py reset_db         # Reset DB (DANGER!)
```

---

## 📤 Crop Image Upload - Example

```python
import requests

# Analyze crop image
with open('tomato.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/crops/analyze/public',
        files={'image': f}
    )
    result = response.json()
    print(result['result']['disease_detected'])
    print(result['result']['treatment'])
```

---

## 🎤 Voice Chat - Example

```python
# Send voice message
with open('question.webm', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/chat/voice',
        files={'audio': f},
        data={'language': 'hi', 'return_audio': 'true'},
        headers={'Authorization': f'Bearer {token}'}
    )
    result = response.json()
    print("You said:", result['transcription'])
    print("AI says:", result['response_text'])
```

---

## 🔌 WebSocket (Real-time Chat)

```javascript
const socket = io('http://localhost:5000');

socket.emit('join_chat', { session_id: 123 });

socket.emit('send_message_ws', {
    user_id: 1,
    session_id: 123,
    message: 'मेरी फसल में पीलापन आ रहा है',
    language: 'hi'
});

socket.on('ai_response', (data) => {
    console.log(data.message);
});

socket.on('ai_typing', (data) => {
    console.log('AI typing:', data.typing);
});
```

---

## 📝 Notes

- All AI features require `OPENAI_API_KEY` in `.env`
- App runs in **demo mode** without API key (mock responses)
- Upload files are stored locally in `uploads/` folder
- For production: use PostgreSQL instead of SQLite
- For production: use cloud storage (S3) for uploads
- Frontend (React/HTML) to be built separately
#   K i s a n S a t h i  
 