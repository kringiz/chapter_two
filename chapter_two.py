import streamlit as st
import os
import requests
from openai import OpenAI
import openai
import random
from gtts import gTTS
from PIL import Image
import json
from datetime import datetime

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Set base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Combined HTML to inject custom CSS for the background, text backgrounds, font color, font sizes, and element styling
st.markdown(
    """
    <style>
    /* Change background image */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://github.com/clarencemun/GA_capstone_taler_swift/blob/main/wallpaper5.jpg?raw=true");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: local;
    }

    /* Adding semi-transparent backgrounds to text widgets for better readability */
    .stTextInput, .stTextArea, .stSelectbox, .stButton, .stSlider, .big-font, .stMarkdown, .stTabs, .stRadio {
        background-color: rgba(255, 255, 255, 0.75); /* Semi-transparent white */
        border-radius: 5px; /* Rounded borders */
        padding: 5px; /* Padding around text */
        margin-bottom: 5px; /* Space between widgets */
        color: #333333; /* Dark grey font color */
        font-size: 25px; /* Increased font size for inputs and buttons */
    }

    /* Specific font size increases for the sidebar elements */
    [data-testid="stSidebar"] .stTextInput, [data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stButton, [data-testid="stSidebar"] .stSlider {
        font-size: 18px; /* Larger font size for sidebar elements */
    }

    /* You can customize font color specifically for titles and headers */
    .stTitle, .stHeader, .big-font {
        color: #2E4053; /* Example: darker shade of blue-grey */
        font-size: 30px; /* Larger font size for titles */
    }

    /* Style for big-font class used for larger text */
    .big-font {
        font-size: 30px !important; /* Ensuring it overrides other styles */
        font-weight: bold;
    }

    /* Style for medium-font class used for medium text */
    .medium-font {
        font-size: 20px !important; /* Ensuring it overrides other styles */
        font-weight: bold;
    }

    /* Style for small-font class used for small text */
    .small-font {
        font-size: 12px !important; /* Ensuring it overrides other styles */
        font-weight: bold;
    }

    /* Ensuring the rest of the container is also covered */
    [data-testid="stSidebar"], [data-testid="stHeader"] {
        background-color: transparent;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add developer credit
st.markdown("""
    <div style="text-align: left;">
        <p class="small-font">Developed by Clarence Mun</p>
    </div>
""", unsafe_allow_html=True)

# Initialise OpenAI client
client = OpenAI()

# Define the list of available genres and languages
genres = [
    "Inspirational Real-Life Stories"
]
languages = ['English', '中文', 'Melayu']

characters = "Kai"

# Initialise message history and image counter
message_history = []
image_counter = 1

# Generate a filename for saving an image
def generate_filename():
    global image_counter
    filename = os.path.join(BASE_DIR, "images", f"generated_image_{image_counter}.jpg")
    image_counter += 1
    return filename

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
    global message_history
    language_prefix = get_language_prefix(language)
    full_input_text = f"{language_prefix}about {input_text}"
    message_history.append({'role': 'user', 'content': full_input_text})

    # Call the GPT model using the client object and handle response correctly
    response = client.chat.completions.create(
        model="gpt-4o",  # You can replace it with "gpt-4-1106-preview" if using GPT-4
        messages=message_history,
        temperature=0.7  # Adjust temperature as needed
    )

    # Accessing the response using the updated object structure
    response_text = response.choices[0].message.content
    message_history.append({'role': 'assistant', 'content': response_text})

    # Accumulate responses in a single string
    story_text = ""
    for msg in message_history:
        if msg['role'] == 'assistant':
            story_text += msg['content']

    return story_text

# Generate images from the story
def generate_images_from_story(story_text):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    images_directory = os.path.join(BASE_DIR, "images", timestamp)
    os.makedirs(images_directory, exist_ok=True)

    paragraphs = story_text.split('\n\n')
    images = []
    
    # Context from the first paragraph
    story_context = paragraphs[0].strip() if paragraphs else ""

    # Loop over paragraphs by step of 3, starting from the first
    for i in range(1, len(paragraphs), 3):
        # Combine three paragraphs for each image
        combined_paragraph = paragraphs[i].strip()
        if i + 1 < len(paragraphs):
            combined_paragraph += " " + paragraphs[i + 1].strip()
        if i + 2 < len(paragraphs):
            combined_paragraph += " " + paragraphs[i + 2].strip()

        if combined_paragraph:
            prompt = f"Generate a realistic, emotionally evocative scene that embodies the themes of second chances and personal growth. Depict a modern, everyday environment—such as a park at sunrise, a softly lit classroom, or a welcoming community space—where individuals are engaging in moments of reflection, connection, or support. The scene should capture meaningful interactions or personal moments that emphasize the emotions involved in starting over. Use soft, natural colors like warm yellows, gentle blues, and calming greens to evoke hope and renewal. The overall style should be warm and approachable, with emotional depth that resonates with a teenage audience, reflecting the maturity and vulnerability of embracing a second chance. Full story context: {story_context} Current focus: {combined_paragraph}"
            image_path = generate_image(prompt, images_directory)
            images.append((combined_paragraph, image_path))

    return images

# Generate an image from a description using DALL-E
def generate_image(description, images_directory):
    global image_counter
    # Generate filename within the provided directory
    filename = f"generated_image_{image_counter}.jpg"
    image_counter += 1
    image_path = os.path.join(images_directory, filename)

    # Fetch and save the image
    response = client.images.generate(
        model="dall-e-3",
        prompt=description,
        size="1024x1024",
        quality="standard",
        n=1
    )
    image_url = response.data[0].url
    image_response = requests.get(image_url)
    if image_response.status_code == 200:
        with open(image_path, "wb") as image_file:
            image_file.write(image_response.content)
    return image_path

# Function to save a story to a JSON file
def save_story_to_json(story_data):
    # Specify the directory for saved stories
    stories_dir = os.path.join(BASE_DIR, "saved_stories")
    json_file_path = os.path.join(stories_dir, "stories
