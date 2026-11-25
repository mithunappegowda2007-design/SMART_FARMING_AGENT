# 🌱 Smart Farming AI Agent

An **agentic AI application** for smart farming advice built with **Python, Flask, and Groq LLM API**. Features a multi-agent architecture with 4 specialized AI agents working together to deliver comprehensive, personalized farming intelligence.

---

## 🤖 Multi-Agent Architecture

| Agent | Capability |
|-------|-----------|
| 🌾 **Crop Advisory Agent** | RAG-powered crop guidelines, seed/fertilizer/harvest advice |
| 🌤️ **Weather & Irrigation Agent** | Real-time weather + AI irrigation scheduling |
| 🔬 **Pest & Disease Agent** | Multimodal image analysis + treatment recommendations |
| 📈 **Market Insights Agent** | Price forecasting, selling strategy, cost optimization |

---

## ✨ Features

- **RAG Knowledge Base** — 25+ agricultural knowledge documents across crops, soil, pests, irrigation, market, and government advisories
- **Real-time Weather** — OpenWeatherMap integration with 5-day forecast
- **Multimodal Pest Detection** — Upload crop images for AI visual diagnosis (LLaMA Vision)
- **Multi-Agent Orchestration** — Master agent routes queries to specialist agents and synthesizes responses
- **Dark-themed Responsive UI** — Sidebar navigation, chat interface, dashboard, and dedicated pages for each agent
- **Ultra-fast Inference** — Groq LLM API for sub-second responses

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
cd smart_farming_agent
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

Get your free Groq API key at: https://console.groq.com/keys  
*(Optional)* Get OpenWeatherMap key at: https://openweathermap.org/api

### 3. Run the application

```bash
python app.py
```

Open http://localhost:5000 in your browser.

---

## 📁 Project Structure

```
smart_farming_agent/
├── app.py                    # Flask application + API routes
├── config.py                 # Configuration (API keys, settings)
├── requirements.txt
├── .env.example              # Environment template
│
├── agents/
│   └── farming_agents.py     # 4 AI agents + master orchestrator
│
├── knowledge_base/
│   └── farming_kb.py         # RAG knowledge base (25+ documents)
│
├── utils/
│   ├── weather.py            # OpenWeatherMap integration
│   └── image_processor.py    # Image upload & Base64 processing
│
├── templates/
│   ├── base.html             # Base layout with sidebar
│   ├── index.html            # Home page
│   ├── dashboard.html        # Multi-agent dashboard
│   ├── chat.html             # AI chat interface
│   ├── crop_advisor.html     # Crop advisory page
│   ├── weather.html          # Weather & irrigation page
│   ├── pest_detection.html   # Pest detection (image upload)
│   └── market_insights.html  # Market price forecasting
│
└── static/
    ├── css/main.css          # Dark-themed responsive stylesheet
    ├── js/main.js            # Sidebar + utilities
    └── uploads/              # Uploaded images (auto-created)
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Master agent — routes to specialist agents |
| POST | `/api/crop-advisory` | Crop Advisory Agent |
| POST | `/api/weather` | Weather + Irrigation Agent |
| POST | `/api/pest-detection` | Pest Detection (supports `multipart/form-data` with image) |
| POST | `/api/market-insights` | Market Insights Agent |
| POST | `/api/multi-agent` | All agents in parallel (dashboard) |

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask 3.0
- **LLM**: Groq API — `llama-3.3-70b-versatile` (chat) + `llama-3.2-11b-vision-preview` (images)
- **RAG**: Custom keyword-based retrieval over agricultural knowledge base
- **Weather**: OpenWeatherMap REST API
- **Image Processing**: Pillow (PIL)
- **Frontend**: Vanilla HTML/CSS/JS (dark theme, responsive)

---

## 📸 Pages

- **Home** (`/`) — Feature overview and agent cards
- **Dashboard** (`/dashboard`) — Run all 4 agents simultaneously
- **AI Chat** (`/chat`) — Conversational interface with farm context
- **Crop Advisor** (`/crop-advisor`) — Detailed crop advisory form
- **Weather** (`/weather`) — Live weather + irrigation schedule
- **Pest Detection** (`/pest-detection`) — Upload image or describe symptoms
- **Market Insights** (`/market-insights`) — Price forecast and selling strategy
