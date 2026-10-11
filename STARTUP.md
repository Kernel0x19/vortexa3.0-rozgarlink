# RozgarLink 3.0 — Quick Start Guide

Welcome to **RozgarLink**. This guide explains how to install dependencies, configure environment variables, run the backend and frontend services, and verify that all agents and connectors are active.

---

## 📋 System Prerequisites

Ensure you have the following installed on your machine:
- **Python**: Version `3.10` or `3.11` (Recommended: Python 3.11)
- **Node.js**: Version `18.x` or `20.x` (with `npm`)
- **Git**

---

## 🏗️ Project Architecture Overview

The repository consists of two main applications:
- **`services/`**: Python FastAPI backend with LangGraph AI chatbot, agent workflows (Hackathon, Internship, Scholarship), SQLite database, and live ingestion connectors (Unstop, Devfolio, MLH, Internshala, AICTE).
- **`app/`**: Next.js 15 frontend with React, Tailwind CSS, Supabase authentication, and interactive dashboard views.

```
votexa3.0-rozgarlink/
├── services/               # FastAPI Backend Service
│   ├── app/
│   │   ├── agents/         # AI Chatbot, Hackathon, Internship agents
│   │   ├── api/routes/     # REST Endpoints
│   │   ├── ingestion/      # Live Connectors (Unstop, Devfolio, MLH, etc.)
│   │   └── main.py         # FastAPI application entrypoint
│   └── rozgarlink.db       # SQLite database
├── app/                    # Next.js 15 Frontend
│   └── app/dashboard/      # Student Dashboard, Hackathons, Internships, Chat
└── STARTUP.md              # This setup guide
```

---

## 🚀 Step 1: Backend Setup (FastAPI)

### 1.1 Open a Terminal in the Workspace Root
Open your terminal (PowerShell, Command Prompt, or Bash) in the project root:

```bash
cd d:\vortexa\votexa3.0-rozgarlink
```

### 1.2 Activate the Python Virtual Environment
Use the project virtual environment (or create a new one):

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.\venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

*(If creating a fresh virtual environment: `python -m venv venv`)*

### 1.3 Install Python Dependencies
```bash
pip install -r requirements.txt
pip install langchain-groq groq httpx uvicorn
```

### 1.4 Configure Backend Environment Variables
Create or verify `services/.env`:

```env
# Application Settings
DEBUG=true
DATABASE_URL=sqlite:///./rozgarlink.db
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
DEV_MODE=true

# AI & LLM (Groq API for Chatbot)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b

# Supabase Authentication
NEXT_PUBLIC_SUPABASE_URL=https://zjjrewfyixutxwmubvlb.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Optional Vector & Notifications
CHROMA_PATH=./chroma_data
```

### 1.5 Run Live Data Ingestion (Sync Live Hackathons & Internships)
Run this one-liner to ingest live data from Unstop, Devfolio, MLH, Internshala, and AICTE into the database:

```bash
cd services
python -c "from app.db.session import SessionLocal; from app.ingestion.pipeline import run_ingestion; print(run_ingestion(SessionLocal()))"
```

### 1.6 Start the FastAPI Backend Server
From the `services/` directory:

```bash
uvicorn app.main:app --reload --port 8000
```

- **Backend API URL**: `http://localhost:8000`
- **Swagger Interactive API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/v1/chat/health`

---

## 💻 Step 2: Frontend Setup (Next.js 15)

Open a **separate terminal** window for the frontend.

### 2.1 Navigate to the Frontend Directory
```bash
cd d:\vortexa\votexa3.0-rozgarlink\app
```

### 2.2 Install Node Dependencies
```bash
npm install
```

### 2.3 Configure Frontend Environment Variables
Create or verify `app/.env`:

```env
NEXT_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://zjjrewfyixutxwmubvlb.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 2.4 Start the Frontend Development Server
```bash
npm run dev
```

The Next.js application will start on:
- **Local Application URL**: `http://localhost:3000` (or `http://localhost:3001` if port 3000 is occupied)

---

## 🌐 Step 3: Accessing the Features

Once both servers are running, open your browser and navigate to:

| Feature | URL | Description |
| :--- | :--- | :--- |
| **Main Dashboard** | [http://localhost:3000/dashboard](http://localhost:3000/dashboard) | Overview of profile, matched opportunities, and tracker |
| **Hackathon Finder** | [http://localhost:3000/dashboard/hackathons](http://localhost:3000/dashboard/hackathons) | Browse live hackathons from Unstop, Devfolio, and MLH with direct registration links |
| **Internship Finder** | [http://localhost:3000/dashboard/internships](http://localhost:3000/dashboard/internships) | Browse live internships from Unstop, Internshala, and AICTE |
| **AI Advisor Chatbot**| [http://localhost:3000/dashboard/chat](http://localhost:3000/dashboard/chat) | Streamed conversational assistance using Groq + RAG |
| **API Documentation** | [http://localhost:8000/docs](http://localhost:8000/docs) | Complete interactive Swagger/OpenAPI documentation |

---

## 🛠️ Common Troubleshooting

### 1. `Port 8000 is in use`
Find and terminate any existing process on port 8000:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

### 2. `Port 3000 is in use`
Next.js will automatically fall back to port `3001`. You can access the UI at `http://localhost:3001`. Alternatively, free port 3000:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process -Force
```

### 3. Missing Groq API Key
If the chatbot fails with authentication errors, ensure `GROQ_API_KEY` is set in `services/.env`.

---

## 🎯 Verification Commands

Run these quick sanity checks in your backend terminal:

```bash
# Test backend root
curl http://localhost:8000/health

# Test hackathon listing
curl -H "X-User-Id: test" http://localhost:8000/api/v1/hackathons?limit=5

# Test internship recommendations
curl -H "X-User-Id: test" http://localhost:8000/api/v1/internships/recommendations?limit=5
```
