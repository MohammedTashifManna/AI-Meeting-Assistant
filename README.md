# 🎙️ AI Meeting Assistant

AI Meeting Assistant is a Retrieval-Augmented Generation (RAG) application that converts meeting recordings into intelligent insights. It transcribes meeting audio, extracts action items and important decisions, generates summaries, stores meeting context in a vector database, and enables users to ask questions about meeting content through a conversational interface.

---

## 🚀 Features

### 🎙 Meeting Audio Transcription
      -Upload meeting recordings (.mp4)
      -Uses Whisper Large V3 for transcription
      
### 📝 Meeting Analysis
      -Extracts:
      -Action Items
      -Important Decisions
      -Meeting Summary
      
### 🔍 RAG-based Question Answering
      -Ask questions about uploaded meetings
      -Retrieves relevant chunks from vector database
      -Generates context-aware answers
      
### 🧠 Semantic Search
      -Uses sentence embeddings
      -Finds relevant meeting discussions
      
### 📄 PDF Report Generation
      -Download meeting analysis report
      
### 👍 Feedback System
      -Thumbs up/down for responses
      
### 💾 Persistent Vector Storage
      -Stores embeddings using ChromaDB 

---

## 🛠️ Tech Stack

### Frontend
- Streamlit

### LLM
- Groq API
- Llama 3.1 8B Instant
- Whisper Large V3

### Speech-to-Text
- Whisper Large V3

### Embeddings
- all-MiniLM-L6-v2

### Vector DataBase
- ChromaDB

### Frameworks & Libraries
- LangChain
- Pydantic
- FPDF
- python-dotenv

---

## ⚙️ Installation

### 1. Clone repository

```bash
git clone https://github.com/yourusername/AI-Meeting-Assistant.git

cd AI-Meeting-Assistant
```

### 2. Create virtual environment

Windows:

```bash
python -m venv venv

venv\Scripts\activate
```

Mac/Linux:

```bash
python3 -m venv venv

source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file

Create a `.env` file in your project root:

```env
GROQ_API_KEY=your_api_key_here
```

---

## ▶️ Run Application

```bash
streamlit run app.py
```

Application will start on:

```bash
http://localhost:8501
```

---

## 📋 How It Works

### Step 1
Upload an MP4 meeting recording.

### Step 2
Whisper Large V3 converts audio into text.

### Step 3
Transcript is split into manageable chunks.

### Step 4
Llama 3.1 analyzes the transcript and extracts:

- Tasks assigned
- Decisions made
- Meeting summary

### Step 5
Generate downloadable PDF report.

### Step 6
Ask Questions about Meeting.

---
## 🔒 Environment Variables

| Variable | Description |
|-----------|-------------|
| GROQ_API_KEY | Groq API key |

---

### 🧠 RAG Pipeline Used
User Query 
    ↓ 
Similarity Search 
    ↓ 
Retrieve Relevant Chunks 
    ↓ 
Provide Context to LLM 
    ↓ 
Generate Answer
