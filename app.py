import streamlit as st
import pandas as pd
import os
import time
from utils import get_personality_string, get_reaction

# Set page configuration
st.set_page_config(
    page_title="TweetPersona",
    page_icon="🐰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-title {
        font-size: 42px;
        font-weight: bold;
        background: linear-gradient(to right, #FF6B6B, #FF8E53);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 20px;
    }
    .personality-container {
        background-color: #f8f1ff;
        border-radius: 10px;
        padding: 20px;
        border: 2px solid #ffcad4;
        margin: 20px 0;
        position: relative;
    }
    .bunny-left {
        position: absolute;
        left: 10px;
        top: 10px;
        font-size: 24px;
    }
    .bunny-right {
        position: absolute;
        right: 10px;
        top: 10px;
        font-size: 24px;
    }
    .personality-text {
        font-size: 18px;
        line-height: 1.6;
        color: #614051;
        text-align: center;
        padding: 10px 40px;
    }
    .reaction-box {
        background-color: #2e2e2e;
        color: white;
        padding: 20px;
        border-radius: 10px;
        font-family: sans-serif;
        font-size: 18px;
        margin-top: 20px;
    }
    .page-subtitle {
        font-size: 24px;
        color: #614051;
        margin-bottom: 15px;
    }
    .file-icon {
        background-color: #ffcad4;
        color: #614051;
        padding: 8px 15px;
        border-radius: 20px;
        display: inline-flex;
        align-items: center;
        margin-top: 10px;
    }
    .file-icon span {
        margin-left: 8px;
    }
    .upload-zone {
        border: 2px dashed #cccccc;
        border-radius: 5px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }
    .upload-zone:hover {
        background-color: #f8f8f8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'df' not in st.session_state:
    st.session_state.df = None
if 'personality_string' not in st.session_state:
    st.session_state.personality_string = None
if 'file_path' not in st.session_state:
    st.session_state.file_path = None
if 'content_text' not in st.session_state:
    st.session_state.content_text = ""
if 'reaction_text' not in st.session_state:
    st.session_state.reaction_text = None
if 'reaction_score' not in st.session_state:
    st.session_state.reaction_score = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = None

# Title
st.markdown('<div class="main-title">TweetPersona: Digital Twin for Audience Insights</div>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page:", ["Home", "Persona Reaction"])

# Function to reset state variables related to reaction
def reset_reaction_state():
    # Delete temporary file if it exists
    if 'file_path' in st.session_state and st.session_state.file_path:
        try:
            if os.path.exists(st.session_state.file_path):
                os.remove(st.session_state.file_path)
                print(f"Removed temporary file: {st.session_state.file_path}")
        except Exception as e:
            print(f"Error removing file: {e}")
    
    # Clear session state variables
    st.session_state.file_path = None
    st.session_state.content_text = ""
    st.session_state.reaction_text = None
    st.session_state.reaction_score = None
    st.session_state.uploaded_file = None
    st.session_state.file_name = None

# Function to reset all state variables
def reset_all_state():
    st.session_state.df = None
    st.session_state.personality_string = None
    reset_reaction_state()

# Home page
if page == "Home":
    st.header("Upload Tweet Data")
    
    uploaded_file = st.file_uploader("Drag and drop your CSV file with tweets", type=["csv"])
    
    if uploaded_file is not None:
        # Reset all state variables when a new file is uploaded
        reset_all_state()
        
        with st.spinner("Analyzing personality..."):
            # Load the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Compute engagement
            df['engagement'] = df['favorite_count'] / df['view_count']
            
            # Save to session state
            st.session_state.df = df
            print("DataFrame loaded and engagement calculated:", st.session_state.df.head())
            
            # Get personality string
            st.session_state.personality_string = get_personality_string(df)
            print("Personality string generated:", st.session_state.personality_string)
            
            time.sleep(1)  # Add a small delay for the spinner to be visible
        
        st.success("Analysis complete!")
    
    # Display personality string if it exists (whether newly uploaded or from previous session)
    if st.session_state.personality_string is not None:
        st.markdown('<div class="page-subtitle">Personality Analysis</div>', unsafe_allow_html=True)
        st.markdown(f'''
        <div class="personality-container">
            <div class="bunny-left">🐰</div>
            <div class="bunny-right">🐰</div>
            <div class="personality-text">{st.session_state.personality_string}</div>
        </div>
        ''', unsafe_allow_html=True)

# Persona Reaction page
elif page == "Persona Reaction":
    st.header("Simulate Persona Reaction")
    
    # Check if personality has been analyzed
    if st.session_state.personality_string is None:
        st.warning("Please upload and analyze tweet data on the Home page first.")
    else:
        # Content input section
        st.markdown('<div class="page-subtitle">Content</div>', unsafe_allow_html=True)
        
        # Text input for content
        content_text = st.text_area("Enter content to get a reaction", value=st.session_state.content_text, height=150)
        st.session_state.content_text = content_text
        
        # File uploader with drag and drop functionality
        uploaded_file = st.file_uploader(
            "Upload a file (PDF or image)",
            type=["pdf", "png", "jpg", "jpeg", "webp"],
            key="reaction_file"
        )
        
        # Handle uploaded file
        if uploaded_file is not None:
            st.session_state.file_name = uploaded_file.name
            
            try:
                # Save uploaded file to a temporary location
                with open(f"temp_{uploaded_file.name}", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.session_state.file_path = f"temp_{uploaded_file.name}"
                
                # Display file icon
                st.markdown(f'<div class="file-icon">📄<span>{uploaded_file.name}</span></div>', unsafe_allow_html=True)
                
                # Display image if file is an image
                file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                if file_extension in ['.png', '.jpg', '.jpeg', '.webp']:
                    st.image(uploaded_file, caption='Uploaded Image', width=400)
            except Exception as e:
                st.error(f"Error saving file: {e}")
                st.session_state.file_path = None
        
        # Reaction and Reset buttons
        col1, col2 = st.columns([1, 1])
        
        with col1:
            react_button = st.button("React")
        
        with col2:
            reset_button = st.button("Reset")
        
        if reset_button:
            reset_reaction_state()
            st.rerun()
        
        # Get reaction when React button is clicked
        if react_button:
            if not st.session_state.content_text and st.session_state.file_path is None:
                st.warning("Please enter content or upload a file to get a reaction.")
            else:
                with st.spinner("Reacting..."):
                    # Make sure file_path is valid before passing to get_reaction
                    file_path = st.session_state.file_path
                    
                    # Check if file exists
                    if file_path is not None and not os.path.exists(file_path):
                        st.error(f"File not found: {file_path}")
                        file_path = None
                    
                    # Call the get_reaction function
                    reaction_result = get_reaction(
                        st.session_state.content_text,
                        st.session_state.file_path,
                        st.session_state.personality_string
                    )
                    
                    # Save the reaction results to session state
                    st.session_state.reaction_text = reaction_result["reaction_text"]
                    st.session_state.reaction_score = reaction_result["reaction_score"]
                    
                    time.sleep(1)  # Add a small delay for the spinner to be visible
        
        # Display reaction if available
        if st.session_state.reaction_text is not None:
            st.markdown('<div class="page-subtitle">Reaction</div>', unsafe_allow_html=True)
            
            # Create two columns for reaction text and score
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Display reaction text
                st.markdown(f'<div class="reaction-box">{st.session_state.reaction_text}</div>', unsafe_allow_html=True)
            
            with col2:
                # Create thermometer with score
                score = st.session_state.reaction_score
                
                # Draw vertical thermometer
                st.markdown("""
                <style>
                    .thermometer-container {
                        width: 60px;
                        height: 300px;
                        background-color: #f0f0f0;
                        border-radius: 15px;
                        position: relative;
                        margin: 0 auto;
                        border: 3px solid #ccc;
                    }
                    .thermometer-fill {
                        position: absolute;
                        bottom: 0;
                        width: 100%;
                        background-color: #ff4d4d;
                        border-radius: 0 0 12px 12px;
                    }
                    .thermometer-mark {
                        position: absolute;
                        left: 70px;
                        font-weight: bold;
                    }
                    .thermometer-score {
                        position: absolute;
                        left: 70px;
                        font-weight: bold;
                        color: #ff4d4d;
                    }
                    .bunny-happy {
                        position: absolute;
                        left: 70px;
                        font-size: 24px;
                    }
                    .bunny-sad {
                        position: absolute;
                        left: 70px;
                        font-size: 24px;
                    }
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="thermometer-container">
                    <div class="thermometer-fill" style="height: {score}%;"></div>
                    <div class="thermometer-mark" style="bottom: 0;">0</div>
                    <div class="thermometer-mark" style="top: 0;">100</div>
                    <div class="thermometer-score" style="bottom: {score}%;">{score}</div>
                    <div class="bunny-happy" style="top: -30px;">🐰</div>
                    <div class="bunny-sad" style="bottom: -30px;">🐰</div>
                </div>
                """, unsafe_allow_html=True)