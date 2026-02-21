# 🛡️ ContentGuard AI — AI Content Moderation Agent
### AgentX 2026 Hackathon | PS 10 | MES Wadia College of Engineering, Pune

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## 🌐 Live Demo
👉 **[https://contentguard-ai.streamlit.app](https://contentguard-ai.streamlit.app)**

---

## 🧠 Agent Workflow

```
User Input (Text / URL / CSV)
        ↓
Platform Policy Selection (6 presets)
        ↓
Groq API → Llama 3.3 70B
        ↓
Risk Scoring Engine (0–100)
        ↓
Category Classifier (8 harmful categories)
        ↓
Autonomous Verdict: ALLOW ✅ / REVIEW ⚠️ / BLOCK 🚫
        ↓
Reasoning + Suggestions + Confidence
        ↓
Appeal System (if REVIEW / BLOCK)
        ↓
Webhook Payload / Analytics Dashboard / CSV Export
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Text Analysis** | Real-time moderation with risk score 0–100 |
| 🌐 **URL Scanner** | Fetches & moderates any public webpage |
| 📦 **Batch Mode** | Upload CSV, moderate all rows automatically |
| ⚖️ **Appeal System** | Users contest decisions with context, agent reconsiders |
| ⚙️ **Policy Builder** | 6 platform presets (Kids, Gaming, News, Health...) |
| 📊 **Live Dashboard** | Analytics, charts, flagged category breakdown |
| 🔌 **Webhook Simulation** | Real API integration payload preview |
| 📥 **CSV Export** | Download full moderation report |

---

## 🏗️ Project Structure

```
content-moderation-agent/
├── app.py                      # Main Streamlit entry point
├── agent/
│   ├── __init__.py
│   └── moderator.py            # Core AI agent logic
├── utils/
│   ├── __init__.py
│   ├── logger.py               # Session log manager
│   ├── exporter.py             # CSV export
│   └── url_scanner.py          # Webpage fetcher
├── config/
│   └── settings.py             # Central configuration
├── components/
│   ├── __init__.py
│   ├── sidebar.py              # Sidebar UI
│   ├── results.py              # Result display
│   └── dashboard.py            # Analytics dashboard
├── .streamlit/
│   ├── config.toml             # Theme config
│   └── secrets.toml            # API keys (local only, gitignored)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🆓 Tech Stack (100% Free)

| Tool | Purpose |
|------|---------|
| Python 3.8+ | Language |
| Groq API | Free LLM inference |
| Llama 3.3 70B | AI model |
| Streamlit | Web UI + Cloud deployment |
| Pandas | Batch CSV processing |

---

## ⚡ Local Setup

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/content-moderation-agent
cd content-moderation-agent

# 2. Install
pip install -r requirements.txt

# 3. Add API key to .streamlit/secrets.toml
GROQ_API_KEY = "gsk_your_key_here"

# 4. Run
python -m streamlit run app.py
```

Get your **free** Groq API key at: https://console.groq.com

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub (public)
2. Go to https://share.streamlit.io
3. Click **"New app"** → select this repo → `app.py`
4. Go to **Advanced Settings → Secrets** and add:
   ```
   GROQ_API_KEY = "gsk_your_actual_key"
   ```
5. Click **Deploy** — live in 2 minutes!

---

## 🎯 PS 10 Requirements — All Met

| Requirement | Status |
|-------------|--------|
| Analyzes user text | ✅ |
| Detects harmful categories | ✅ 8 categories |
| Assigns risk scores | ✅ 0–100 |
| Decides allow/review/block | ✅ |
| With explanation | ✅ Full reasoning + suggestions |

---

*Built for AgentX 2026 @ MES Wadia College of Engineering, Pune*