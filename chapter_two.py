import streamlit as st
import os
from openai import AzureOpenAI
import random
from gtts import gTTS
import json
from datetime import datetime

# Set up Azure OpenAI API key and endpoint
os.environ["AZURE_OPENAI_API_KEY"] = st.secrets["AZURE_OPENAI_API_KEY"]

# Set base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Font size slider for dynamic adjustment
font_size = st.sidebar.slider("Adjust Font Size", min_value=10, max_value=40, value=20)

# Inject custom CSS to adjust font size dynamically based on slider
st.markdown(
    f"""
    <style>
    /* Dynamic font size adjustment for all text elements */
    .dynamic-font {{
        font-size: {font_size}px !important;
    }}

    /* Change background image */
    [data-testid="stAppViewContainer"] {{
        background-image: url("https://github.com/clarencemun/GA_capstone_taler_swift/blob/main/wallpaper5.jpg?raw=true");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: local;
    }}

    /* Adding semi-transparent backgrounds to text widgets for better readability */
    .stTextInput, .stTextArea, .stSelectbox, .stButton, .stSlider, .big-font, .stMarkdown, .stTabs, .stRadio {{
        background-color: rgba(255, 255, 255, 0.75); /* Semi-transparent white */
        border-radius: 5px; /* Rounded borders */
        padding: 5px; /* Padding around text */
        margin-bottom: 5px; /* Space between widgets */
        color: #333333; /* Dark grey font color */
    }}

    /* Style for big-font class used for larger text */
    .big-font {{
        font-size: 30px !important;
        font-weight: bold;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# Add app name with correct font size
st.markdown(f'<div class="dynamic-font" style="text-align: center;"><h1>Chapter Two</h1></div>', unsafe_allow_html=True)

# Add developer credit
st.markdown("""
    <div class="dynamic-font" style="text-align: left;">
        <p>Developed by Clarence Mun</p>
    </div>
""", unsafe_allow_html=True)

# Initialise Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=st.secrets["AZURE_ENDPOINT"],
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  # Ensure API key is stored securely in environment variables
    api_version=st.secrets["AZURE_API_VERSION"]
)

# Initialise session state for message history and generated story
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if 'generated_story' not in st.session_state:
    st.session_state['generated_story'] = None

# Initialize session state for stories
if 'stories' not in st.session_state:
    st.session_state['stories'] = []

# Chat with the language model
def chat_with_model(input_text):
    message_history = st.session_state['message_history']
    message_history.append({'role': 'user', 'content': input_text})

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=message_history,
        temperature=0.7
    )

    response_text = response.choices[0].message.content
    message_history.append({'role': 'assistant', 'content': response_text})
    st.session_state['message_history'] = message_history
    return response_text

# Function to save a story to session state
def save_story(story_data):
    st.session_state['stories'].append(story_data)
    st.success("Story saved successfully!")

# Generate a story with the specified parameters
def generate_story(name, setting, conflict, rebuilding, support, emotional_tone, timeframe, resolution_style):
    prompt = (
        f"Write an inspirational real-life story about an ex-offender named {name}, who is rebuilding their life after a period of incarceration."
        f"The story is set in {setting}, with a focus on their family and community."
        f"The main conflict centers on {conflict} and the emotional struggles of the ex-offender and their family."
        f"The rebuilding process involves {rebuilding} and is influenced by {support}."
        f"The emotional tone of the story should be {emotional_tone}."
        f"The ex-offender has been reintegrating into their family for {timeframe}."
        f"The story should conclude with {resolution_style}, emphasizing the power of second chances, forgiveness, and family unity."
        f"Ensure the content of the story and language complexity are age-appropriate for students aged 13 to 16."
    )

    with st.spinner(f"Generating your story..."):
        story_text = chat_with_model(prompt)
    
    if story_text:
        st.session_state['generated_story'] = story_text

        story_data = {
            "name": name,
            "setting": setting,
            "conflict": conflict,
            "rebuilding": rebuilding,
            "support": support,
            "emotional_tone": emotional_tone,
            "timeframe": timeframe,
            "resolution_style": resolution_style,
            "text": story_text
        }

        save_story(story_data)
    else:
        st.error("The story generation did not return any text. Please try again.")

# Function to display the story
def display_story():
    if 'generated_story' in st.session_state and st.session_state['generated_story']:
        story_text = st.session_state['generated_story']
        # Display each paragraph of the story text with dynamic font size
        for paragraph in story_text.split('\n'):
            st.markdown(f'<div class="dynamic-font">{paragraph}</div>', unsafe_allow_html=True)

# Sidebar for input configuration (shared across tabs)
with st.sidebar:
    st.title("Configuration")

# Main tabs
tab1, tab2 = st.tabs(["Rebirth", "Reflect"])

# Tab 1: Custom Story Generator (Rebirth)
with tab1:
    st.markdown("### Generate Your Story")

    # Story Input Parameters
    name = st.text_input("Enter the main character's name", value="Kai")
    setting = st.text_input("Story setting (e.g. Family home, community)", value="family home and community")
    conflict = st.text_input("Main conflict (e.g. Stigma, emotional struggle)", value="the stigma faced by the family and the emotional struggle of reintegration")
    rebuilding = st.text_input("Rebuilding process (e.g. rebuilding relationships, gaining trust)", value="rebuilding relationships and trust")
    support = st.selectbox("Support system involved", ["None", "Therapy", "Religious guidance", "Community support"], index=3)
    emotional_tone = st.selectbox("Emotional tone", ["Hopeful", "Bittersweet", "Reflective", "Determined"], index=0)
    timeframe = st.selectbox("Reintegration timeframe", ["Just returned", "A few months", "A year", "Several years"], index=0)
    resolution_style = st.selectbox("Resolution style", ["Positive resolution", "Ongoing struggles", "Open-ended"], index=0)

    if st.button("Generate Story"):
        generate_story(name, setting, conflict, rebuilding, support, emotional_tone, timeframe, resolution_style)

# Tab 2: Display Previously Saved Stories (Reflect)
with tab2:
    st.write("(Story Archive)")
    if st.session_state['stories']:
        for story in st.session_state['stories']:
            with st.expander(f"{story['name']} - {story['setting']}"):
                for paragraph in story["text"].split('\n'):
                    st.markdown(f'<div class="dynamic-font">{paragraph}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Conflict: {story["conflict"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Rebuilding: {story["rebuilding"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Support: {story["support"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Resolution Style: {story["resolution_style"]}</div>', unsafe_allow_html=True)
    else:
        st.write("No previous stories found.")
