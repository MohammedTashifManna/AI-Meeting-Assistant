# 🎙️ AI Meeting Assistant

An AI-powered Meeting Assistant built with Streamlit, Groq, Whisper, and LangChain that automatically transcribes meeting recordings and extracts meaningful insights such as action items, decisions, and summaries.

---

## 🚀 Features

✅ Upload MP4 meeting recordings  
✅ Automatic speech-to-text transcription using Whisper Large V3  
✅ AI-generated structured meeting analysis  
✅ Extracts:

- Action Items
- Important Decisions
- Meeting Summary

✅ Download analysis report as PDF  
✅ Feedback system (thumbs up/down)  
✅ Chat-style UI using Streamlit  
✅ Handles large meeting recordings  

---

## 🛠️ Tech Stack

### Frontend
- Streamlit

### AI / LLM
- Groq API
- Llama 3.1 8B Instant
- Whisper Large V3

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

---
## 🔒 Environment Variables

| Variable | Description |
|-----------|-------------|
| GROQ_API_KEY | Groq API key |

---
