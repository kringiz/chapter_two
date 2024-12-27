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

# Function to display the story
def display_story():
    if 'generated_story' in st.session_state and st.session_state['generated_story']:
        story_text = st.session_state['generated_story']
        # Display each paragraph of the story text with dynamic font size
        for paragraph in story_text.split('\n'):
            st.markdown(f'<div class="dynamic-font">{paragraph}</div>', unsafe_allow_html=True)

# Generate a story with the specified parameters
def generate_story(name, setting, second_chance, impact, support, story_style, timeframe, resolution_style):
    prompt = (
        f"Write an emotional first-person narrative about my experience as {name}, an ex-offender returning home. "
        f"I am living in {setting}, trying to rebuild connections with my family and community. "
        f"Through {second_chance}, I found hope for a new beginning. "
        f"My journey has {impact}, and it's deeply personal watching these changes unfold. "
        f"The {support} I receive has taught me about humility and acceptance. "
        f"Tell my story in a {story_style} way, revealing my inner thoughts and personal growth. "
        f"It's been {timeframe} since I came home, and each day brings new challenges and victories. "
        f"The story should end with {resolution_style}, showing how second chances and forgiveness can transform a person. "
        f"Write for young readers (13-16), focusing on themes of redemption and family bonds."
    )

    with st.spinner(f"Generating your story..."):
        story_text = chat_with_model(prompt)
    
    if story_text:
        st.session_state['generated_story'] = story_text

        story_data = {
            "name": name,
            "setting": setting,
            "second_chance": second_chance,
            "impact": impact,
            "support": support,
            "story_style": story_style,
            "timeframe": timeframe,
            "resolution_style": resolution_style,
            "perspective": "first-person",
            "text": story_text
        }

        save_story(story_data)
    else:
        st.error("The story generation did not return any text. Please try again.")

# Add new function for third-person story generation
def generate_story_third_person(name, setting, second_chance, impact, support, story_style, timeframe, resolution_style):
    prompt = (
        f"Write an observant third-person narrative about {name}, watching their reintegration journey unfold. "
        f"In {setting}, their presence creates ripples through family and community relationships. "
        f"When offered {second_chance}, the community witnesses their determination to change. "
        f"Their transformation {impact}, showing how one person's journey affects many lives. "
        f"Through {support}, others learn about forgiveness and growth. "
        f"Tell their story in a {story_style} way, observing changes in family dynamics and community attitudes. "
        f"After {timeframe} of their return, the neighborhood has seen significant changes. "
        f"The narrative concludes with {resolution_style}, demonstrating how community support enables healing. "
        f"Keep the story suitable for young readers (13-16), emphasizing community transformation and collective healing."
    )

    with st.spinner(f"Generating your story..."):
        story_text = chat_with_model(prompt)
    
    if story_text:
        st.session_state['generated_story'] = story_text

        story_data = {
            "name": name,
            "setting": setting,
            "second_chance": second_chance,
            "impact": impact,
            "support": support,
            "story_style": story_style,
            "timeframe": timeframe,
            "resolution_style": resolution_style,
            "perspective": "third-person",
            "text": story_text
        }

        save_story(story_data)
    else:
        st.error("The story generation did not return any text. Please try again.")

# Sidebar for input configuration (shared across tabs)
with st.sidebar:
    st.title("Configuration")

# Main tabs
tab1, tab2, tab3 = st.tabs(["Forgive Me", "Forgive You", "Archive"])

# Tab 1: Custom Story Generator (Rebirth)
with tab1:
    st.markdown("### Generate Your Story (First Person)")

    # Story Input Parameters
    name = st.text_input("Enter the main character's name", value="Kai")
    setting = st.text_input("Story setting (e.g. Family home, community)", value="family home and community")
    second_chance = st.text_input("Second chance offered (e.g. Job opportunity by an empathetic employer)", value="a job opportunity offered by a former teacher")
    impact = st.text_input("Impact on relationships (e.g. Family support, community acceptance)", value="strengthening family bonds and rebuilding trust with neighbors", key="impact_first")
    support = st.selectbox("Support system involved", ["None", "Family", "Therapy", "Religious guidance", "Community support"], index=1)
    story_style = st.selectbox("Style of story", [
        "Reflective and thoughtful",
        "Journey of redemption",
        "Family reconciliation",
        "Community healing",
        "Personal transformation",
        "Hope and resilience"
    ], index=0)
    timeframe = st.selectbox("Reintegration timeframe", ["Just returned", "A few months", "A year", "Several years"], index=0)
    resolution_style = st.selectbox("Resolution style", ["Positive resolution", "Ongoing struggles", "Open-ended"], index=0)

    if st.button("Generate Story"):
        generate_story(name, setting, second_chance, impact, support, story_style, timeframe, resolution_style)
        display_story()

# Add new third person story tab
with tab2:
    st.markdown("### Generate Their Story (Third Person)")
    
    # Story Input Parameters (identical fields)
    name = st.text_input("Enter the main character's name", value="Kai", key="name_third")
    setting = st.text_input("Story setting (e.g. Family home, community)", value="family home and community", key="setting_third")
    second_chance = st.text_input("Second chance offered (e.g. Job opportunity by an empathetic employer)", value="a job opportunity offered by a former teacher", key="second_chance_third")
    impact = st.text_input("Impact on relationships (e.g. Family support, community acceptance)", value="strengthening family bonds and rebuilding trust with neighbors", key="impact_third")
    support = st.selectbox("Support system involved", ["None", "Therapy", "Religious guidance", "Community support"], index=3, key="support_third")
    story_style = st.selectbox("Style of story", [
        "Reflective and thoughtful",
        "Journey of redemption",
        "Family reconciliation",
        "Community healing",
        "Personal transformation",
        "Hope and resilience"
    ], index=0, key="story_style_third")
    timeframe = st.selectbox("Reintegration timeframe", ["Just returned", "A few months", "A year", "Several years"], index=0, key="time_third")
    resolution_style = st.selectbox("Resolution style", ["Positive resolution", "Ongoing struggles", "Open-ended"], index=0, key="resolution_third")

    if st.button("Generate Story", key="generate_third"):
        generate_story_third_person(name, setting, second_chance, impact, support, story_style, timeframe, resolution_style)
        display_story()

# Tab 2: Display Previously Saved Stories (Reflect)
with tab3:
    st.write("(Story Archive)")
    if st.session_state['stories']:
        for story in st.session_state['stories']:
            with st.expander(f"{story['name']} - {story['second_chance']}"):
                for paragraph in story["text"].split('\n'):
                    st.markdown(f'<div class="dynamic-font">{paragraph}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Second Chance: {story["second_chance"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Impact: {story["impact"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Support: {story["support"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Resolution Style: {story["resolution_style"]}</div>', unsafe_allow_html=True)
    else:
        st.write("No previous stories found.")
