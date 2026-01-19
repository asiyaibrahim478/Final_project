# app.py
import streamlit as st
import anthropic
import os
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

# Custom CSS for blue background and styling
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Content container */
    .main-container {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 2rem auto;
        max-width: 900px;
    }
    
    /* Header styling */
    .header-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: #718096;
        margin-bottom: 2rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #e2e8f0;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2d3748;
        color: white;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #a855f7 0%, #ec4899 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        width: 100%;
        font-size: 1.1rem;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #9333ea 0%, #db2777 100%);
        border: none;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    /* Slider styling */
    .stSlider {
        padding: 1rem 0;
    }
    
    /* Summary output box */
    .summary-box {
        background-color: #f7fafc;
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    
    /* Logo styling */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1rem;
    }
    
    .logo-text {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2d3748;
    }
    </style>
""", unsafe_allow_html=True)

# Helper Functions
def get_summary_from_ai(text, api_key, length_instruction):
    """Generate summary using Claude AI"""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"Please provide a {length_instruction} summary of the following text. Focus on the main points and key information:\n\n{text}"
                }
            ]
        )
        return message.content[0].text
    except Exception as e:
        raise Exception(f"AI Error: {str(e)}")

def extract_text_from_url(url):
    """Extract text content from a URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        raise Exception(f"URL Error: {str(e)}")

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise Exception(f"PDF Error: {str(e)}")

def get_youtube_video_id(url):
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_youtube_transcript(video_id):
    """Get transcript from YouTube video"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([item['text'] for item in transcript_list])
        return transcript_text
    except Exception as e:
        raise Exception(f"YouTube Error: Could not retrieve transcript. {str(e)}")

def transcribe_audio(audio_file):
    """Transcribe audio file to text"""
    try:
        recognizer = sr.Recognizer()
        
        # Convert audio to wav format if needed
        audio = AudioSegment.from_file(audio_file)
        audio = audio.set_channels(1).set_frame_rate(16000)
        
        # Export to wav
        wav_io = io.BytesIO()
        audio.export(wav_io, format='wav')
        wav_io.seek(0)
        
        # Transcribe
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        return text
    except Exception as e:
        raise Exception(f"Audio Error: {str(e)}")

# Sidebar
with st.sidebar:
    st.markdown("""
        <div class="logo-container">
            <span style="font-size: 2rem;">📦</span>
            <span class="logo-text">Summary Box</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🏠 Dashboard")
    st.markdown("### 🛠️ Tools")
    with st.expander("Tools Menu", expanded=True):
        st.markdown("- Summarizer")
        st.markdown("- Paragraph Writer")
        st.markdown("- Paraphraser")
        st.markdown("- Writing Tips")
        st.markdown("- Explain Like I'm 5")
    
    st.markdown("### 📚 Collections")
    with st.expander("Collections Menu"):
        st.markdown("- Favorites")
    
    st.markdown("### 👥 Invite Friends")
    
    st.markdown("---")
    st.markdown("#### API Configuration")
    api_key = st.text_input("Anthropic API Key", type="password", help="Enter your Anthropic API key")

# Main content
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown('<h1 class="header-title">Content Summarizer</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Get the gist of any content with one click!</p>', unsafe_allow_html=True)

# Length map for all tabs
length_map = {
    1: "very brief (2-3 sentences)",
    2: "brief (4-5 sentences)",
    3: "moderate (1 paragraph)",
    4: "detailed (2 paragraphs)",
    5: "comprehensive (3+ paragraphs)"
}

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Text", "🔗 URL", "📄 PDF", "🎵 Audio", "📺 YouTube"])

# TAB 1: TEXT SUMMARIZATION
with tab1:
    st.markdown("### Enter Your Text")
    
    # Summary length slider
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown("**Shorter**")
    with col2:
        summary_length_text = st.slider("Summary Length", 1, 5, 3, label_visibility="collapsed", key="text_slider")
    with col3:
        st.markdown("**Longer**")
    
    # Text input area
    text_input = st.text_area(
        "Paste your text here",
        height=300,
        placeholder="Paste the text you want to summarize here...",
        label_visibility="collapsed"
    )
    
    # Action buttons
    col1, col2 = st.columns([1, 4])
    with col1:
        clear_btn_text = st.button("Clear", key="clear_text")
    with col2:
        summarize_btn_text = st.button("Summarize ➔", key="summarize_text")
    
    if clear_btn_text:
        st.rerun()
    
    if summarize_btn_text:
        if not text_input.strip():
            st.error("Please enter some text to summarize!")
        elif not api_key:
            st.error("Please enter your Anthropic API key in the sidebar!")
        else:
            with st.spinner("Generating summary..."):
                try:
                    length_instruction = length_map[summary_length_text]
                    summary = get_summary_from_ai(text_input, api_key, length_instruction)
                    
                    st.markdown("### 📋 Summary")
                    st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                    
                    st.download_button(
                        label="📥 Download Summary",
                        data=summary,
                        file_name="summary.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# TAB 2: URL SUMMARIZATION
with tab2:
    st.markdown("### Enter URL to Summarize")
    
    # Summary length slider
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown("**Shorter**")
    with col2:
        summary_length_url = st.slider("Summary Length", 1, 5, 3, label_visibility="collapsed", key="url_slider")
    with col3:
        st.markdown("**Longer**")
    
    url_input = st.text_input(
        "Enter URL",
        placeholder="https://example.com/article",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        clear_btn_url = st.button("Clear", key="clear_url")
    with col2:
        summarize_btn_url = st.button("Summarize ➔", key="summarize_url")
    
    if clear_btn_url:
        st.rerun()
    
    if summarize_btn_url:
        if not url_input.strip():
            st.error("Please enter a URL!")
        elif not api_key:
            st.error("Please enter your Anthropic API key in the sidebar!")
        else:
            with st.spinner("Fetching and summarizing content..."):
                try:
                    # Extract text from URL
                    text_content = extract_text_from_url(url_input)
                    
                    if len(text_content) < 50:
                        st.error("Could not extract enough text from this URL. Please try another URL.")
                    else:
                        # Generate summary
                        length_instruction = length_map[summary_length_url]
                        summary = get_summary_from_ai(text_content, api_key, length_instruction)
                        
                        st.markdown("### 📋 Summary")
                        st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                        
                        st.download_button(
                            label="📥 Download Summary",
                            data=summary,
                            file_name="url_summary.txt",
                            mime="text/plain"
                        )
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# TAB 3: PDF SUMMARIZATION
with tab3:
    st.markdown("### Upload PDF File")
    
    # Summary length slider
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown("**Shorter**")
    with col2:
        summary_length_pdf = st.slider("Summary Length", 1, 5, 3, label_visibility="collapsed", key="pdf_slider")
    with col3:
        st.markdown("**Longer**")
    
    pdf_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        label_visibility="collapsed"
    )
    
    st.info("📄 Files must be in PDF format and under 10MB.")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        clear_btn_pdf = st.button("Clear", key="clear_pdf")
    with col2:
        summarize_btn_pdf = st.button("Summarize ➔", key="summarize_pdf")
    
    if clear_btn_pdf:
        st.rerun()
    
    if summarize_btn_pdf:
        if not pdf_file:
            st.error("Please upload a PDF file!")
        elif not api_key:
            st.error("Please enter your Anthropic API key in the sidebar!")
        else:
            with st.spinner("Extracting text and generating summary..."):
                try:
                    # Extract text from PDF
                    text_content = extract_text_from_pdf(pdf_file)
                    
                    if len(text_content) < 50:
                        st.error("Could not extract enough text from this PDF.")
                    else:
                        # Generate summary
                        length_instruction = length_map[summary_length_pdf]
                        summary = get_summary_from_ai(text_content, api_key, length_instruction)
                        
                        st.markdown("### 📋 Summary")
                        st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                        
                        st.download_button(
                            label="📥 Download Summary",
                            data=summary,
                            file_name="pdf_summary.txt",
                            mime="text/plain"
                        )
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# TAB 4: AUDIO SUMMARIZATION
with tab4:
    st.markdown("### Upload Audio File")
    
    # Summary length slider
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown("**Shorter**")
    with col2:
        summary_length_audio = st.slider("Summary Length", 1, 5, 3, label_visibility="collapsed", key="audio_slider")
    with col3:
        st.markdown("**Longer**")
    
    audio_file = st.file_uploader(
        "Choose an audio file",
        type=['wav', 'mp3', 'm4a', 'ogg', 'flac'],
        label_visibility="collapsed"
    )
    
    st.info("🎵 Supported formats: WAV, MP3, M4A, OGG, FLAC")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        clear_btn_audio = st.button("Clear", key="clear_audio")
    with col2:
        summarize_btn_audio = st.button("Summarize ➔", key="summarize_audio")
    
    if clear_btn_audio:
        st.rerun()
    
    if summarize_btn_audio:
        if not audio_file:
            st.error("Please upload an audio file!")
        elif not api_key:
            st.error("Please enter your Anthropic API key in the sidebar!")
        else:
            with st.spinner("Transcribing audio and generating summary..."):
                try:
                    # Transcribe audio
                    text_content = transcribe_audio(audio_file)
                    
                    if len(text_content) < 10:
                        st.error("Could not transcribe enough content from this audio.")
                    else:
                        # Generate summary
                        length_instruction = length_map[summary_length_audio]
                        summary = get_summary_from_ai(text_content, api_key, length_instruction)
                        
                        st.markdown("### 📋 Summary")
                        st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                        
                        st.download_button(
                            label="📥 Download Summary",
                            data=summary,
                            file_name="audio_summary.txt",
                            mime="text/plain"
                        )
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# TAB 5: YOUTUBE SUMMARIZATION
with tab5:
    st.markdown("### Enter YouTube URL")
    
    # Summary length slider
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown("**Shorter**")
    with col2:
        summary_length_yt = st.slider("Summary Length", 1, 5, 3, label_visibility="collapsed", key="yt_slider")
    with col3:
        st.markdown("**Longer**")
    
    youtube_url = st.text_input(
        "Enter YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )
    
    st.info("📺 Enter a YouTube video URL with available captions/subtitles")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        clear_btn_yt = st.button("Clear", key="clear_yt")
    with col2:
        summarize_btn_yt = st.button("Summarize ➔", key="summarize_yt")
    
    if clear_btn_yt:
        st.rerun()
    
    if summarize_btn_yt:
        if not youtube_url.strip():
            st.error("Please enter a YouTube URL!")
        elif not api_key:
            st.error("Please enter your Anthropic API key in the sidebar!")
        else:
            with st.spinner("Fetching transcript and generating summary..."):
                try:
                    # Extract video ID
                    video_id = get_youtube_video_id(youtube_url)
                    if not video_id:
                        st.error("Invalid YouTube URL. Please check and try again.")
                    else:
                        # Get transcript
                        text_content = get_youtube_transcript(video_id)
                        
                        # Generate summary
                        length_instruction = length_map[summary_length_yt]
                        summary = get_summary_from_ai(text_content, api_key, length_instruction)
                        
                        st.markdown("### 📋 Summary")
                        st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                        
                        st.download_button(
                            label="📥 Download Summary",
                            data=summary,
                            file_name="youtube_summary.txt",
                            mime="text/plain"
                        )
                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: white; padding: 1rem;">
        <p>Made with ❤️ using Streamlit and Claude AI</p>
    </div>
    """,
    unsafe_allow_html=True
)
