import streamlit as st
import os
import requests
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
    .dynamic-font {{
        font-size: {font_size}px !important;
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

# Define the list of available genres and languages
genres = [
    "Inspirational Real-Life Stories"
]
languages = ['English', '中文', 'Melayu']

characters = "Kai"

# Initialise message history
message_history = []

# Get language prefix for story generation
def get_language_prefix(language):
    if language == '中文':
        return "请用纯中文写一个故事"
    elif language == 'Melayu':
        return "Sila tulis cerita dalam bahasa Melayu penuh, tiada perkataan Inggeris"
    else:
        return "Create a story"

# Generate speech from text using gTTS
def generate_speech(text, filename='story.mp3', language='en', directory="audio"):
    directory = os.path.join(BASE_DIR, directory)
    if selected_language == '中文':
        language = 'zh'
    elif selected_language == 'Melayu':
        language = 'id'
    else:
        language = 'en'

    myobj = gTTS(text=text, lang=language, slow=False)

    if not os.path.exists(directory):
        os.makedirs(directory)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"story_{timestamp}.mp3"
    file_path = os.path.join(directory, filename)

    myobj.save(file_path)
    st.audio(file_path, format='audio/mp3', start_time=0)

# Chat with the language model
def chat_with_model(input_text, language):
    global message_history
    language_prefix = get_language_prefix(language)
    full_input_text = f"{language_prefix} about {input_text}"
    message_history.append({'role': 'user', 'content': full_input_text})

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",  
        messages=message_history,
        temperature=0.7
    )

    response_text = response.choices[0].message.content
    message_history.append({'role': 'assistant', 'content': response_text})

    story_text = ""
    for msg in message_history:
        if msg['role'] == 'assistant':
            story_text += msg['content']

    return story_text

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
        with open(json_file_path, "w") as file:
            json.dump(data, file, indent=4)
        st.success("Story saved successfully!")
    except Exception as e:
        st.error(f"Failed to save story: {e}")

# Function to load all stories from a JSON file
def load_stories_from_json():
    stories_dir = os.path.join(BASE_DIR, "saved_stories")
    json_file_path = os.path.join(stories_dir, "stories.json")
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

# Updated story generation with relevant themes
def generate_story(story_type, main_character, setting, conflict, resolution, moral, length_minutes, include_audio, selected_language):
    prompt = (
        f"Write an {story_type} that reflects personal growth, second chances, and overcoming challenges. "
        f"The main character, {main_character}, is anonymous, and their personal identity or background specifics should not be revealed. "
        f"The story is set in {setting}, focusing on the family dealing with the absence of a parent due to incarceration and the process of rebuilding after their return. "
        f"The conflict is {conflict}, highlighting societal stigma and the emotional challenges within the family. "
        f"The resolution is {resolution}, focusing on themes of personal responsibility, forgiveness, and community support. "
        f"The moral of the story is '{moral}', aimed at encouraging reflection and promoting empathy, understanding, and growth. "
        f"Ensure the content of the story and language complexity are age-appropriate for students aged 13 to 16. "
        f"Keep the story length around {200 * length_minutes} words."
    )

    with st.spinner(f"Generating your story..."):
        story_text = chat_with_model(prompt, selected_language)
    
    if story_text:
        st.success("Story generated successfully!")

        story_data = {
            "story_type": story_type,
            "main_character": main_character,
            "setting": setting,
            "conflict": conflict,
            "resolution": resolution,
            "moral": moral,
            "length_minutes": length_minutes,
            "text": story_text,
            "include_audio": include_audio,
            "language": selected_language
        }
        
        save_story_to_json(story_data)

        for paragraph in story_text.split('\n'):
            st.markdown(f'<div class="dynamic-font">{paragraph}</div>', unsafe_allow_html=True)
            
        if include_audio == "Yes":
            with st.spinner("Generating audio..."):
                generate_speech(story_text)
            st.success("Audio generated successfully!")
        
    else:
        st.error("The story generation did not return any text. Please try again.")

# Sidebar configuration
with st.sidebar:
    st.title("Configuration")
    selected_language = st.selectbox("Select Language:", languages)
    include_audio = st.radio("Include Audio?", ["No", "Yes"])
    length_minutes = st.slider("Length of story (minutes):", 1, 10, 5)

# Genre and Character Configurations
genre_choice = st.sidebar.radio("Genre:", ["Random", "Manual"])
if genre_choice == "Manual":
    story_type = st.sidebar.selectbox("Select Genre", genres)
else:
    story_type = random.choice(genres)
    st.sidebar.write(f"Random Genre: {story_type}")

character_choice = st.sidebar.radio("Main Character:", ["Random", "Manual"])
if character_choice == "Manual":
    main_character = st.sidebar.text_input("Enter Main Character's Name", "")
else:
    main_character = characters
    st.sidebar.write(f"Random Main Character")

# New Parameters related to family and ex-offender themes
setting = st.sidebar.text_input("Setting:", value="A small family home in a close-knit community.")
conflict = st.sidebar.text_input("Conflict:", value="The stigma faced by the family due to the parent's past and the emotional struggle with reintegration.")
resolution = st.sidebar.text_input("Resolution:", value="The family learns to forgive and rebuild their relationships while overcoming societal judgment.")
moral = st.sidebar.text_input("Moral:", value="Second chances, the importance of forgiveness, and the strength of family.")

# Main tabs
tab1, tab2, tab3 = st.tabs(["Rebirth", "Renew", "Reflect"])

# Tab 1: Generate Random Story
with tab1:
    if st.button("Generate Random Story"):
        random_setting = 'Singapore'
        random_conflict = 'The family faces judgement from the community.'
        random_resolution = 'The family reconnects, learning to forgive.'
        random_moral = 'The power of second chances and forgiveness.'
        generate_story(story_type, main_character, random_setting, random_conflict, random_resolution, random_moral, length_minutes, include_audio, selected_language)

# Tab 2: Generate Custom Story
with tab2:
    if st.button("Generate Custom Story"):
        generate_story(story_type, main_character, setting, conflict, resolution, moral, length_minutes, include_audio, selected_language)

# Tab 3: Display Previously Saved Stories
with tab3:
    st.write("(Story Archive)")
    previous_stories = load_stories_from_json()
    if previous_stories:
        for story in previous_stories:
            with st.expander(f"{story['story_type']} - {story['main_character']}"):
                for paragraph in story["text"].split('\n'):
                    st.markdown(f'<div class="dynamic-font">{paragraph}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Genre: {story['story_type']}, Main Character: {story['main_character']}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Setting: {story['setting']}, Conflict: {story['conflict']}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Resolution: {story['resolution']}, Moral: {story['moral']}</div>', unsafe_allow_html=True)
    else:
        st.write("No previous stories found.")
