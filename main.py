import streamlit as st
import time
import tempfile
from fpdf import FPDF
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    st.error("Missing GROQ API Key")
    st.stop()

class ActionItem(BaseModel):

    assignee: str = Field(description="Person responsible for the task")
    task: str = Field(description="Specific task assigned")
    deadline: str = Field(description="Deadline if mentioned")
    priority: str = Field(description="Priority level")


class ImportantDecision(BaseModel):
    decision: str = Field(description="What was the decision taken in the meeting")
    reason: str = Field(description="why was that decision made in the meeting")


class MeetingAnalysis(BaseModel):
    action_items: List[ActionItem]
    important_decisions: List[ImportantDecision]
    summary: List[str]

llm = ChatGroq(temperature=0.3, model="llama-3.1-8b-instant")
structured_llm = llm.with_structured_output(MeetingAnalysis)
client = Groq()
st.title("AI Meeting Assistant")


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

if "history" not in st.session_state:
    st.session_state.history = []

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
uploaded_file = st.file_uploader("Upload your Meeting Recordings: ", type=["mp4"])

if "processed_file" not in st.session_state:
    st.session_state.processed_file = None

if uploaded_file is not None:
    if uploaded_file.type != "video/mp4":
        st.error("Only MP4 video files are allowed")
        st.stop()
    if uploaded_file.size > 200 * 1024 * 1024:
        st.error("File too large")
        st.stop()
    if uploaded_file.name != st.session_state.processed_file:

        st.session_state.processed_file = uploaded_file.name

        # process file

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        with st.spinner("Please Wait While i gather all the information from your meeting...", show_time=True):

            # with st.chat_message("user"):
            # st.session_state.history.append({"role": "assistant", "content": "Gathering all information from the file... Please Wait"})

            # loader = AssemblyAIAudioTranscriptLoader(
            #     file_path=temp_file_path
            # )
            #
            # docs = loader.load()


            try:
                with open(temp_file_path, "rb") as file:

                    transcript = client.audio.transcriptions.create(
                        file=file,
                        model="whisper-large-v3"
                    )
                    transcription=transcript.text
            except Exception as e:
                st.error(f"Error occurred: {e}")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=100,
                add_start_index=True,
            )
            chunks = text_splitter.split_text(transcription)
            # Display the result
            # transcription = docs[0].page_content
            # st.subheader("Transcript")
            # st.write(transcription)
            Meeting_Analysis_Prompt = ChatPromptTemplate.from_template("""
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
                    """)

            meeting_analysis_chain = Meeting_Analysis_Prompt | structured_llm
            Analysis_response = meeting_analysis_chain.invoke({
                "transcript": chunks
            })
            formatted_output = format_meeting_analysis(Analysis_response)
            with st.chat_message("assistant"):
                response = st.write_stream(chat_stream(formatted_output))
                pdf = FPDF()
                pdf.add_page()

                pdf.set_auto_page_break(auto=True, margin=15)

                pdf.set_font("Arial", size=12)

                pdf.multi_cell(0, 10, formatted_output)

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

                os.remove(temp_file_path)
