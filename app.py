# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
from youtube_transcript_api import YouTubeTranscriptApi
import re
import speech_recognition as sr
from pydub import AudioSegment

# Page configuration
st.set_page_config(
    page_title="Summary Box - Content Summarizer",
    page_icon="📦",
    layout="wide"
)

# ================== CSS ==================
st.markdown("""
<style>
.stApp {
    background: #ffffff;
}
[data-testid="stSidebar"] {
    background-color: #f8f9fa;
}
.main-container {
    background-color: white;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 2rem auto;
    max-width: 900px;
}
.summary-box {
    background-color: #f7fafc;
    border-left: 4px solid #667eea;
    padding: 1.5rem;
    border-radius: 8px;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ================== DUMMY SUMMARIZER ==================
def get_summary(text, length):
    sentences = re.split(r'(?<=[.!?]) +', text)
    if length == 1:
        return " ".join(sentences[:2])
    elif length == 2:
        return " ".join(sentences[:4])
    elif length == 3:
        return " ".join(sentences[:6])
    elif length == 4:
        return " ".join(sentences[:8])
    else:
        return " ".join(sentences[:12])

# ================== HELPERS ==================
def extract_text_from_url(url):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator=" ")

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    return " ".join(page.extract_text() for page in reader.pages)

def get_youtube_video_id(url):
    match = re.search(r"(?:v=|youtu.be/)([^&]+)", url)
    return match.group(1) if match else None

def get_youtube_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join(item["text"] for item in transcript)

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_file(audio_file)
    audio = audio.set_channels(1).set_frame_rate(16000)
    wav = io.BytesIO()
    audio.export(wav, format="wav")
    wav.seek(0)
    with sr.AudioFile(wav) as source:
        audio_data = recognizer.record(source)
    return recognizer.recognize_google(audio_data)

# ================== SIDEBAR ==================
with st.sidebar:
    st.title("📦 Summary Box")
    st.markdown("Simple content summarizer (No API needed)")

# ================== MAIN ==================
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.title("Content Summarizer")

length_map = {
    1: "Very Short",
    2: "Short",
    3: "Medium",
    4: "Long",
    5: "Very Long"
}

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📝 Text", "🔗 URL", "📄 PDF", "🎵 Audio", "📺 YouTube"]
)

# ---------- TEXT ----------
with tab1:
    length = st.slider("Summary Length", 1, 5, 3)
    text = st.text_area("Enter text", height=250)
    if st.button("Summarize"):
        if text.strip():
            summary = get_summary(text, length)
            st.markdown("### Summary")
            st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

# ---------- URL ----------
with tab2:
    length = st.slider("Summary Length", 1, 5, 3, key="url")
    url = st.text_input("Enter URL")
    if st.button("Summarize URL"):
        if url:
            text = extract_text_from_url(url)
            summary = get_summary(text, length)
            st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

# ---------- PDF ----------
with tab3:
    length = st.slider("Summary Length", 1, 5, 3, key="pdf")
    pdf = st.file_uploader("Upload PDF", type="pdf")
    if st.button("Summarize PDF"):
        if pdf:
            text = extract_text_from_pdf(pdf)
            summary = get_summary(text, length)
            st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

# ---------- AUDIO ----------
with tab4:
    length = st.slider("Summary Length", 1, 5, 3, key="audio")
    audio = st.file_uploader("Upload Audio", type=["wav", "mp3", "m4a"])
    if st.button("Summarize Audio"):
        if audio:
            text = transcribe_audio(audio)
            summary = get_summary(text, length)
            st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

# ---------- YOUTUBE ----------
with tab5:
    length = st.slider("Summary Length", 1, 5, 3, key="yt")
    yt = st.text_input("YouTube URL")
    if st.button("Summarize Video"):
        video_id = get_youtube_video_id(yt)
        if video_id:
            text = get_youtube_transcript(video_id)
            summary = get_summary(text, length)
            st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
