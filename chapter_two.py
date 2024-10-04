import streamlit as st
import os
import json
from openai import AzureOpenAI
from gtts import gTTS
from datetime import datetime

# Set up Azure OpenAI API key and endpoint
os.environ["AZURE_OPENAI_API_KEY"] = st.secrets["AZURE_OPENAI_API_KEY"]

# Set base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialise Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=st.secrets["AZURE_ENDPOINT"], 
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=st.secrets["AZURE_API_VERSION"]
)

# Define the list of available genres and languages
genres = ["Inspirational Real-Life Stories"]
languages = ['English', '中文', 'Melayu']

# Initialise message history
if 'message_history' not in st.session_state:
    st.session_state.message_history = []

# Check if the story is already in session state
if 'story_text' not in st.session_state:
    st.session_state.story_text = ""

# Font size slider for dynamic adjustment
font_size = st.sidebar.slider("Adjust Font Size", min_value=10, max_value=40, value=20)

# Apply the dynamic font size CSS
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

# Add app name and developer credit
st.markdown(f'<div class="dynamic-font" style="text-align: center;"><h1>Chapter Two</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="dynamic-font" style="text-align: left;"><p>Developed by Clarence Mun</p></div>', unsafe_allow_html=True)

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

# Chat with the language model
def chat_with_model(input_text, language):
    language_prefix = get_language_prefix(language)
    full_input_text = f"{language_prefix} about {input_text}"
    st.session_state.message_history.append({'role': 'user', 'content': full_input_text})

    # Call the GPT model using the client object and handle response correctly
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",  # Azure OpenAI model
        messages=st.session_state.message_history,
        temperature=0.7  # Adjust temperature as needed
    )

    # Accessing the response using the updated object structure
    response_text = response.choices[0].message.content
    st.session_state.message_history.append({'role': 'assistant', 'content': response_text})
    
    return response_text

# Generate a story with the specified parameters
def generate_story(story_type, main_character, setting, conflict, resolution, moral, length_minutes, include_audio, selected_language):
    prompt = (
        f"Write an {story_type} that reflects personal growth, second chances, and overcoming challenges."
        f"The main character, {main_character}, is anonymous, and their personal identity or background specifics should not be revealed."
        f"The story is set in {setting}, focusing on the general experience of learning from mistakes and seeking redemption."
        f"The conflict is {conflict}, but do not describe any graphic or explicit details. Focus on the emotional and psychological aspects of overcoming adversity."
        f"The resolution is {resolution}, highlighting themes of personal responsibility, forgiveness, and community support."
        f"The moral of the story is '{moral}', aimed at encouraging reflection and promoting empathy, understanding, and growth."
        f"Ensure the content of the story and language complexity are age-appropriate for students aged 13 to 16. Avoid any content that could be potentially traumatising or unsuitable."
        f"Keep the story length around {200 * length_minutes} words. Keep each paragraph to 4 sentences."
        f"Display only the story."
    )

    # Generate story text
    with st.spinner(f"Generating your story..."):
        st.session_state.story_text = chat_with_model(prompt, selected_language)

# Sidebar for input configuration
with st.sidebar:
    st.title("Configuration")
    selected_language = st.selectbox("Select Language:", languages)
    include_audio = st.radio("Include Audio?", ["No", "Yes"])
    length_minutes = st.slider("Length of story (minutes):", 1, 10, 5)

# Genre Configuration
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
    st.sidebar.write(f"Random Main Character")

# Story Generation Section
if st.button("Generate Story"):
    random_setting = 'Singapore'
    random_conflict = 'random conflict'
    random_resolution = 'random resolution'
    random_moral = 'a random moral lesson'
    generate_story(story_type, main_character, random_setting, random_conflict, random_resolution, random_moral, length_minutes, include_audio, selected_language)

# Display the generated story with dynamic font size
if st.session_state.story_text:
    for paragraph in st.session_state.story_text.split('\n'):
        st.markdown(f'<div class="dynamic-font">{paragraph}</div>', unsafe_allow_html=True)

# Generating speech for the plain text if audio is included
if include_audio == "Yes" and st.session_state.story_text:
    with st.spinner("Generating audio..."):
        generate_speech(st.session_state.story_text)
    st.success("Audio generated successfully!")
