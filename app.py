# app.py
import streamlit as st
import anthropic
import os

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

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Text", "🔗 URL", "📄 PDF", "🎵 Audio", "📺 YouTube"])

with tab1:
    st.markdown("### Enter Your Text")
    
    # Summary length slider
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown("**Shorter**")
    with col2:
        summary_length = st.slider("Summary Length", 1, 5, 3, label_visibility="collapsed")
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
        clear_btn = st.button("Clear")
    with col2:
        summarize_btn = st.button("Summarize ➔")
    
    # Handle clear button
    if clear_btn:
        st.rerun()
    
    # Handle summarize button
    if summarize_btn:
        if not text_input.strip():
            st.error("Please enter some text to summarize!")
        elif not api_key:
            st.error("Please enter your Anthropic API key in the sidebar!")
        else:
            with st.spinner("Generating summary..."):
                try:
                    # Initialize Anthropic client
                    client = anthropic.Anthropic(api_key=api_key)
                    
                    # Determine summary length instruction
                    length_map = {
                        1: "very brief (2-3 sentences)",
                        2: "brief (4-5 sentences)",
                        3: "moderate (1 paragraph)",
                        4: "detailed (2 paragraphs)",
                        5: "comprehensive (3+ paragraphs)"
                    }
                    length_instruction = length_map[summary_length]
                    
                    # Create summary using Claude
                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1000,
                        messages=[
                            {
                                "role": "user",
                                "content": f"Please provide a {length_instruction} summary of the following text. Focus on the main points and key information:\n\n{text_input}"
                            }
                        ]
                    )
                    
                    # Extract summary
                    summary = message.content[0].text
                    
                    # Display summary
                    st.markdown("### 📋 Summary")
                    st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Summary",
                        data=summary,
                        file_name="summary.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")

with tab2:
    st.info("🔗 URL summarization feature - Coming soon!")
    st.markdown("This feature will allow you to summarize content from any web URL.")

with tab3:
    st.info("📄 PDF summarization feature - Coming soon!")
    st.markdown("Upload PDF files and get instant summaries. Files must be in PDF format and under 10MB.")

with tab4:
    st.info("🎵 Audio summarization feature - Coming soon!")
    st.markdown("This feature will transcribe and summarize audio files.")

with tab5:
    st.info("📺 YouTube summarization feature - Coming soon!")
    st.markdown("This feature will summarize YouTube videos by analyzing transcripts.")

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
