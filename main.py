import streamlit as st
import time
import tempfile
from fpdf import FPDF
import os
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from typing import Optional

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    st.error("Missing GROQ API Key")
    st.stop()

st.title("AI Meeting Assistant")

if "history" not in st.session_state:
    st.session_state.history = []

if "processed_file" not in st.session_state:
    st.session_state.processed_file = None

class ActionItem(BaseModel):

    assignee: Optional[str] = Field(description="Person responsible for the task")
    task: Optional[str] = Field(description="Specific task assigned")
    deadline: Optional[str] = Field(description="Deadline if mentioned")
    priority: Optional[str] = Field(description="Priority level")


class ImportantDecision(BaseModel):
    decision: str = Field(description="What was the decision taken in the meeting")
    reason: Optional[str] = Field(default="Not Mentioned", description="why was that decision made in the meeting")


class MeetingAnalysis(BaseModel):
    action_items: List[ActionItem]
    important_decisions: List[ImportantDecision]
    summary: List[str]

llm = ChatGroq(temperature=0.3, model="llama-3.1-8b-instant")
structured_llm = llm.with_structured_output(MeetingAnalysis)
client = Groq()

Meeting_Analysis_Prompt = PromptTemplate.from_template(
    """
        You are an expert AI Meeting Assistant.

        Analyze the transcript carefully.

        Extract:
        1. Action Items
        2. Important Decisions
        3. Short Meeting Summary


        Rules:
        - Be accurate
        - If information is missing, write "Not Mentioned"
        - Use markdown formatting
        - Provide a concise summary in few bullet points.

        Transcript:
        {transcript}
        """
)
ans_prompt = PromptTemplate.from_template(
    template="""
                   Answer using this context:

                   {context}

                   User question:
                   {prompt}
                   """)

def chat_stream(prompt_response):

    lines = prompt_response.split("\n")

    for line in lines:
        yield line + "\n"
        time.sleep(0.05)


def save_feedback(index):
    st.session_state.history[index]["feedback"] = st.session_state[f"feedback_{index}"]

def format_meeting_analysis(data):
    output = ""

    # -------------------------
    # Action Items
    # -------------------------
    output += "Action Items\n"
    output += "-" * 40 + "\n"

    for item in data.action_items:
        output += f"- assignee: {item.assignee}, \n"
        output += f"  Task: {item.task}, \n"
        output += f"  Deadline: {item.deadline}, \n"
        output += f"  Priority: {item.priority}.\n\n"

    # -------------------------
    # Important Decisions
    # -------------------------
    output += "\nImportant Decisions\n"
    output += "-" * 40 + "\n"

    for decision in data.important_decisions:
        output += f"- Decision: {decision.decision}, \n"
        output += f"  Reason: {decision.reason}.\n\n"

    # -------------------------
    # Summary
    # -------------------------
    output += "\nMeeting Summary\n"
    output += "-" * 40 + "\n"

    for point in data.summary:
        output += f"- {point}\n"

    return output


def process_upload(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name
    try:
        with open(temp_file_path, "rb") as file:

            transcript = client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3"
            )
            transcription = transcript.text
    except Exception as e:
        st.error(f"Error occurred: {e}")

    return transcription


def chunking_process(transcription):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        add_start_index=True,
    )
    chunks = text_splitter.split_text(transcription)
    documents = [Document(page_content=chunk) for chunk in chunks]
    return documents

def analysis_report(chunks):
    transcript_text = "\n".join([doc.page_content for doc in chunks])
    meeting_analysis_chain = Meeting_Analysis_Prompt | structured_llm
    Analysis_response = meeting_analysis_chain.invoke({"transcript": transcript_text})
    formatted_output = format_meeting_analysis(Analysis_response)
    return formatted_output


def search_query(prompt):
    results = vectorstore.similarity_search(prompt,k=5) #k=5, top 5 matches
    context = "\n".join(
        [doc.page_content for doc in results]
    )

    chain = ans_prompt | llm
    doc = chain.invoke({"context": context, "prompt": prompt})

    return doc.content
model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
persist_directory = "./chroma_db"
vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=model
)

uploaded_file = st.file_uploader("Upload your Meeting Recordings: ", type=["mp4"])
for i, message in enumerate(st.session_state.history):
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant":
            feedback = message.get("feedback", None)
            st.session_state[f"feedback_{i}"] = feedback
            st.feedback(
                "thumbs",
                key=f"feedback_{i}",
                disabled=feedback is not None,
                on_change=save_feedback,
                args=[i],
            )
if uploaded_file is not None:
    if uploaded_file.type != "video/mp4":
        st.error("Only MP4 video files are allowed")
        st.stop()
    if uploaded_file.size > 200 * 1024 * 1024:
        st.error("File too large")
        st.stop()
    if uploaded_file.name != st.session_state.processed_file:
        st.session_state.processed_file = uploaded_file.name
    with st.spinner("Please Wait While i gather all the information from your meeting...", show_time=True):

        transcript_data = process_upload(uploaded_file)
        chunk_data = chunking_process(transcript_data)
        vectorstore.add_documents(chunk_data)
        analysed_report = analysis_report(chunk_data)
        with st.chat_message("assistant"):
            response = st.write_stream(chat_stream(analysed_report))
            pdf = FPDF()
            pdf.add_page()

            pdf.set_auto_page_break(auto=True, margin=15)

            pdf.set_font("Arial", size=12)

            pdf.multi_cell(0, 10, analysed_report)

            # Convert to bytes
            pdf_bytes = pdf.output(dest="S").encode("latin-1")

            st.download_button(
                label="Download Report",
                data=pdf_bytes,
                file_name="Meeting_Analysis_Report.pdf",
                mime="application/pdf",
                on_click="ignore",
                icon="📥"
            )
            st.feedback(
                "thumbs",
                key=f"feedback_{len(st.session_state.history)}",
                on_change=save_feedback,
                args=[len(st.session_state.history)],
            )

if prompt := st.chat_input("Say something"):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        search_ans = search_query(prompt)
        response = st.write_stream(chat_stream(search_ans))
        st.feedback(
            "thumbs",
            key=f"feedback_{len(st.session_state.history)}",
            on_change=save_feedback,
            args=[len(st.session_state.history)],
        )
    st.session_state.history.append({"role": "assistant", "content": response})
