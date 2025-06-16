# GenCallAI: AI-Powered Call Routing and Analysis System

---

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture & Workflow](#architecture--workflow)
- [Tech Stack](#tech-stack)
- [Key Components](#key-components)
  - [1. app.py (Streamlit App)](#1-apppy-streamlit-app)
  - [2. call_analyzer.py (Deep AI & Audio Analysis)](#2-call_analyzerpy-deep-ai--audio-analysis)
  - [3. utils/agent_matching.py (Agent Matching & Scheduling)](#3-utilsagent_matchingpy-agent-matching--scheduling)
  - [4. Database Layer](#4-database-layer)
  - [5. API Layer (FastAPI)](#5-api-layer-fastapi)
- [How to Run](#how-to-run)
- [Folder Structure](#folder-structure)
- [Extending the Project](#extending-the-project)

---

## Project Overview
GenCallAI is an end-to-end AI-driven system for analyzing customer calls, extracting actionable insights, and intelligently routing calls to the best-suited agents. It is designed for insurance, customer support, and similar domains where efficient, context-aware call handling is critical.

---

## Architecture & Workflow
1. **Audio Upload**: User uploads a call audio file via the Streamlit app (`app.py`).
2. **Transcription & Deep AI Analysis**: The audio is transcribed and analyzed for sentiment, urgency, intent, and metadata using advanced NLP and audio feature extraction (`call_analyzer.py`).
3. **Agent Matching**: The system matches the best agent using AI-driven logic (`utils/agent_matching.py`).
4. **Scheduling & Recording**: The call is scheduled, and all data is stored in a SQLite database.
5. **Dashboards & APIs**: Managers and agents can view schedules, call histories, and analytics via Streamlit dashboards (`frontend.py`, `app.py`) or REST APIs (`api.py`).

---

## Tech Stack
### Backend & Data
- **Python 3**
- **FastAPI**: REST API backend
- **SQLite**: Lightweight relational database
- **pydub, librosa**: Audio processing
- **speechrecognition**: Speech-to-text
- **spaCy, transformers, TextBlob, KeyBERT**: NLP, sentiment, intent, and metadata extraction
- **numpy, pandas**: Data manipulation

### Frontend
- **Streamlit**: Rapid dashboard and UI prototyping

### Other
- **Uvicorn**: ASGI server for FastAPI
- **Shell scripting**: For orchestration (`run_all.sh`)

---

## Key Components

### 1. `app.py` (Streamlit App)
- **Purpose**: Main user interface for uploading audio, viewing transcriptions, analyzing calls, and assigning agents.
- **Features**:
  - Uploads and plays audio files (MP3)
  - Converts audio to WAV for transcription
  - Uses Google Speech Recognition for transcription
  - Calls `CallAnalyzer` for deep analysis (sentiment, urgency, intent, metadata, language proficiency, audio features)
  - Displays all results in a user-friendly format
  - Allows agent matching and scheduling with a single click
  - Shows agent schedules and client call histories
- **Tech Stack**: Streamlit, pydub, speechrecognition, pandas, custom CSS for UI

### 2. `call_analyzer.py` (Deep AI & Audio Analysis)
- **Purpose**: This is the core AI engine for the project, responsible for extracting actionable insights from both the audio and its transcription.
- **Detailed Features**:
  - **Text Analysis**:
    - **Sentiment Analysis**: Uses TextBlob for polarity and a HuggingFace emotion classifier for nuanced emotion detection.
    - **Urgency Detection**: Keyword-based detection of urgency levels (high, medium, low) from the transcription.
    - **Intent Detection**: Rule-based and keyword-driven, e.g., detecting claim-related or general inquiries.
    - **Metadata Extraction**: Combines spaCy NER, regex, and KeyBERT to extract names, claim IDs, and claim types from the transcription.
  - **Audio Feature Extraction**:
    - Uses librosa to extract features such as RMS energy (loudness), zero-crossing rate (calmness), MFCCs (timbre), and duration.
    - These features are used to refine sentiment and urgency, e.g., loud or agitated speech can increase urgency or negative sentiment.
  - **Emotion Detection**:
    - Uses HuggingFace transformers (distilroberta-base) to classify emotions in the text, providing a more granular understanding than simple polarity.
  - **Language Proficiency Estimation**:
    - Heuristic based on average word length, lexical diversity, and grammar accuracy (via TextBlob correction).
    - Maps to levels: "Advanced", "Intermediate", "Basic", "Beginner".
  - **Combined Sentiment**:
    - Fuses text-based and audio-based cues for a more robust sentiment score, e.g., neutral text but high loudness = likely negative.
  - **Extensibility**:
    - Modular design allows easy addition of new NLP or audio features.
- **Tech Stack**: spaCy, transformers (HuggingFace), TextBlob, librosa, KeyBERT, numpy

### 3. `utils/agent_matching.py` (Agent Matching & Scheduling)
- **Purpose**: AI-driven logic for matching the best agent and scheduling calls.
- **Features**:
  - **Agent Scoring**: Considers urgency, intent, agent proficiency, specialization, tiredness, and workload.
  - **Priority Queue**: Schedules calls based on urgency using Python's `heapq` for real-time prioritization.
  - **Database Integration**: Updates agent status, records calls, and manages schedules.
  - **Extensible**: Easy to add new matching criteria (e.g., language, region).
- **Tech Stack**: Python, heapq (priority queue), datetime, custom database functions

### 4. Database Layer
- **Files**: `database/agent_database.py`, `database/client_database.py`
- **Purpose**: Stores all agents, clients, calls, and schedules in SQLite databases
- **Features**:
  - Agent and client tables with rich metadata
  - Call history and scheduling tables
  - Easy initialization with mock data (`intialize_databases.py`)
- **Tech Stack**: SQLite, Python (sqlite3)

### 5. API Layer (FastAPI)
- **File**: `api.py`
- **Purpose**: Exposes REST endpoints for agents, clients, schedules, and call histories
- **Features**:
  - Get agent/client details, schedules, and call histories
  - CORS enabled for frontend integration
- **Tech Stack**: FastAPI, Python

---

## How to Run
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Initialize databases**:
   ```bash
   python intialize_databases.py
   ```
3. **Run all services**:
   ```bash
   bash run_all.sh
   ```
4. **Access the apps**:
   - Use `app.py` (Streamlit) for uploading and analyzing calls, and agent assignment.
   - Use `frontend.py` (Streamlit) for dashboards and management views.
   - Use `api.py` (FastAPI) for programmatic access to agent/client/call data.

---

## Folder Structure
```
AI-CALL-ROUTING/
├── app.py                  # Streamlit app for call upload, analysis, and agent assignment
├── api.py                  # FastAPI backend for REST APIs
├── call_analyzer.py        # Deep AI and audio analysis logic
├── frontend.py             # Streamlit dashboard for agents/clients
├── intialize_databases.py  # Script to initialize SQLite databases
├── requirements.txt        # Python dependencies
├── run_all.sh              # Script to launch all services
├── database/
│   ├── agent_database.py   # Agent DB logic
│   ├── client_database.py  # Client DB logic
│   └── data/               # SQLite DB files
├── utils/
│   └── agent_matching.py   # Agent matching and scheduling logic
```

---

## Extending the Project
- Add new agent matching criteria (e.g., language, region, experience)
- Integrate with external telephony APIs for real-time call ingestion
- Enhance NLP with more advanced models (BERT, GPT, etc.)
- Add analytics and reporting dashboards
- Deploy with Docker or cloud services

---

## Authors & Credits
- Built with ❤️ using Python, FastAPI, Streamlit, and open-source AI libraries.

---

For questions or contributions, please open an issue or pull request!
