import streamlit as st
import os
import requests
from azure.ai.openai import AzureOpenAI
import random
from gtts import gTTS
from PIL import Image
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
def get_azure_openai_client():
    return AzureOpenAI(
        azure_endpoint="https://epi-gpt-4-0125-preview.openai.azure.com/", 
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),  # Ensure API key is stored securely in environment variables
        api_version="2024-02-01"
    )

# Define the list of available genres and languages
genres = [
    "Inspirational Real-Life Stories"
]
languages = ['English', '中文', 'Melayu']

characters = "Kai"

# Initialise message history
message_history = []

# Generate speech from text using gTTS
def generate_speech(text, filename='story.mp3', language='en', directory="audio"):
    directory = os.path.join(BASE_DIR, directory)
    if selected_language == '中文':
        language = 'zh'
    elif selected_language == 'Melayu':
        language = 'id'
    else:
        language = 'en'

    # Create the text-to-speech object
    myobj = gTTS(text=text, lang=language, slow=False)

    # Check if the directory exists, and create it if it doesn't
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Generate a filename with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"story_{timestamp}.mp3"
    file_path = os.path.join(directory, filename)

    # Save the converted audio
    myobj.save(file_path)

    # Play the converted file using 'open' on macOS
    st.audio(file_path, format='audio/mp3', start_time=0)

# Chat with Azure OpenAI model
def ChatGPT4(system_prompt, user_prompt, model_name="gpt-4-0125-preview"):
    client = get_azure_openai_client()
    response = client.chat.completions.create(
        model=model_name, 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=4000
    )
    return response.choices[0].message.content

# Function to generate a story using Azure OpenAI
def generate_story(story_type, main_character, setting, conflict, resolution, moral, length_minutes, include_illustrations, include_audio, selected_language):
    system_prompt = f"You are a helpful assistant. Write an {story_type} that reflects personal growth, second chances, and overcoming challenges."
    user_prompt = (
        f"The main character, {main_character}, is anonymous, and their personal identity or background specifics should not be revealed."
        f"The story is set in {setting}, focusing on the general experience of learning from mistakes and seeking redemption."
        f"The conflict is {conflict}, but do not describe any graphic or explicit details. Focus on the emotional and psychological aspects of overcoming adversity."
        f"The resolution is {resolution}, highlighting themes of personal responsibility, forgiveness, and community support."
        f"The moral of the story is '{moral}', aimed at encouraging reflection and promoting empathy, understanding, and growth."
        f"Ensure the content of the story and language complexity are age-appropriate for students aged 13 to 16. Avoid any content that could be potentially traumatising or unsuitable."
        f"Keep the story length around {200 * length_minutes} words."
    )

    with st.spinner("Generating your story..."):
        story_text = ChatGPT4(system_prompt, user_prompt, model_name="gpt-4")

    if story_text:
        st.success("Story generated successfully!")

        # Display the generated story
        for paragraph in story_text.split('\n'):
            st.markdown(f'<div class="dynamic-font">{paragraph}</div>', unsafe_allow_html=True)

        # Optionally generate speech for the story
        if include_audio == "Yes":
            with st.spinner("Generating audio..."):
                generate_speech(story_text)
            st.success("Audio generated successfully!")
    else:
        st.error("The story generation did not return any text. Please try again.")

# Function to save a story to a JSON file
def save_story_to_json(story_data):
    stories_dir = os.path.join(BASE_DIR, "saved_stories")
    json_file_path = os.path.join(stories_dir, "stories.json")

    if not os.path.exists(stories_dir):
        os.makedirs(stories_dir)

    try:
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as file:
                data = json.load(file)
            data.append(story_data)
        else:
            data = [story_data]
        # Save updated data
        with open(json_file_path, "w") as file:
            json.dump(data, file, indent=4)
        st.success("Story saved successfully!")
    except Exception as e:
        st.error(f"Failed to save story: {e}")

# Function to load all stories from a JSON file
def load_stories_from_json():
    stories_dir = os.path.join(BASE_DIR, "saved_stories")
    json_file_path = os.path.join(stories_dir, "stories.json")
    
    if not os.path.exists(stories_dir):
        os.makedirs(stories_dir)

    try:
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as file:
                data = json.load(file)
            return data
        else:
            return []
    except Exception as e:
        st.error(f"Failed to load stories: {e}")
        return []

# Sidebar for input configuration
with st.sidebar:
    st.title("Configuration")
    selected_language = st.selectbox("Select Language:", languages)
    include_illustrations = st.radio("Include Illustrations?", ["No", "Yes"])
    include_audio = st.radio("Include Audio?", ["No", "Yes"])
    length_minutes = st.slider("Length of story (minutes):", 1, 10, 5)

# Genre and main character configurations
genre_choice = st.sidebar.radio("Genre:", ["Random", "Manual"])
if genre_choice == "Manual":
    story_type = st.sidebar.selectbox("Select Genre", genres)
else:
    story_type = random.choice(genres)
    st.sidebar.write(f"Random Genre: {story_type}")

# Main Character Configuration
character_choice = st.sidebar.radio("Main Character:", ["Random", "Manual"])
if character_choice == "Manual":
    main_character = st.sidebar.text_input("Enter Main Character's Name", "")
else:
    main_character = characters
    st.sidebar.write(f"Random Main Character: {main_character}")

# Main tabs for story generation
tab1, tab2, tab3 = st.tabs(["Rebirth", "Renew", "Reflect"])

# Tab 1: Generate Random Story
with tab1:
    if st.button("Generate Random Story"):
        random_setting = 'Singapore'
        random_conflict = 'random conflict'
        random_resolution = 'random resolution'
        random_moral = 'a random moral lesson'
        generate_story(story_type, main_character, random_setting, random_conflict, random_resolution, random_moral, length_minutes, include_illustrations, include_audio, selected_language)

# Tab 2: Custom Story Generation
with tab2:
    setting = st.text_input("Where the story takes place:")
    conflict = st.text_input("Main plot challenge:", help="Describe the central conflict or challenge that drives the story.")
    resolution = st.text_input("Story Climax and Conclusion:", help="Explain how the plot reaches its peak and resolves.")
    moral = st.text_input("Moral of the story:")
    if st.button("Generate Custom Story"):
        generate_story(story_type, main_character, setting, conflict, resolution, moral, length_minutes, include_illustrations, include_audio, selected_language)

# Tab 3: Story Archive
with tab3:
    st.write("(Story Archive)")
    previous_stories = load_stories_from_json()
    if previous_stories:
        for story in previous_stories:
            with st.expander(f"{story['story_type']} - {story['main_character']}"):
                for paragraph in story["text"].split('\n'):
                    st.markdown(f'<div class="dynamic-font">{paragraph}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Genre: {story["story_type"]}, Main Character: {story["main_character"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Setting: {story["setting"]}, Conflict: {story["conflict"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Resolution: {story["resolution"]}, Moral: {story["moral"]}</div>', unsafe_allow_html=True)
    else:
        st.write("No previous stories found.")
