import streamlit as st
import os
import requests
from openai import OpenAI
import random
from gtts import gTTS
from PIL import Image
import json
from datetime import datetime

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

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
    full_input_text = f"{language_prefix} about {input_text}"
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
    json_file_path = os.path.join(stories_dir, "stories.json")

    # Ensure the directory exists
    if not os.path.exists(stories_dir):
        os.makedirs(stories_dir)

    try:
        # Load existing data
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
    
# Generate a story with the specified parameters
def generate_story(story_type, main_character, setting, conflict, resolution, moral, length_minutes, include_illustrations, include_audio, selected_language):
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

    # Using the spinner to show processing state for story generation
    with st.spinner(f"Generating your story..."):
        story_text = chat_with_model(prompt, selected_language)
    
    if story_text:
        st.success("Story generated successfully!")

        # Prepare data to be saved
        story_data = {
            "story_type": story_type,
            "main_character": main_character,
            "setting": setting,
            "conflict": conflict,
            "resolution": resolution,
            "moral": moral,
            "length_minutes": length_minutes,
            "text": story_text,
            "include_illustrations": include_illustrations,
            "include_audio": include_audio,
            "language": selected_language
        }
        
        # Save the story data
        save_story_to_json(story_data)
        
        # Check if illustrations are included
        if include_illustrations == "Yes":
            with st.spinner("Generating illustrations..."):
                paragraph_image_pairs = generate_images_from_story(story_text)
            for paragraph, image_path in paragraph_image_pairs:
                if image_path:  # Ensure the image was generated successfully
                    # Display the image with plain text caption (no HTML)
                    st.image(image_path, caption=paragraph, use_column_width=True)
            st.success("Illustrations generated successfully!")

            # Generating speech without displaying the text
            if include_audio == "Yes":
                with st.spinner("Generating audio..."):
                    generate_speech(story_text)
                st.success("Audio generated successfully!")

        else:
            # Display each paragraph of the story text with dynamic font size
            for paragraph in story_text.split('\n'):
                st.markdown(f'<div class="dynamic-font">{paragraph}</div>', unsafe_allow_html=True)
            
            # Generating speech for the plain text
            if include_audio == "Yes":
                with st.spinner("Generating audio..."):
                    generate_speech(story_text)
                st.success("Audio generated successfully!")
        
    else:
        st.error("The story generation did not return any text. Please try again.")

# Sidebar for input configuration (shared across tabs)
with st.sidebar:
    st.title("Configuration")
    selected_language = st.selectbox("Select Language:", languages)
    include_illustrations = st.radio("Include Illustrations?", ["No", "Yes"])
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

# Main tabs
tab1, tab2, tab3 = st.tabs(["Rebirth", "Renew", "Reflect"])

# Tab 1: Generate Random Story
with tab1:
    if st.button("Generate Random Story"):
        random_setting = 'Singapore'
        random_conflict = 'random conflict'
        random_resolution = 'random resolution'
        random_moral = 'a random moral lesson'
        generate_story(story_type, main_character, random_setting, random_conflict, random_resolution, random_moral, length_minutes, include_illustrations, include_audio, selected_language)

# Tab 2: Generate Story
with tab2:
    setting = st.text_input("Where the story takes place:")
    conflict = st.text_input("Main plot challenge:", help="Describe the central conflict or challenge that drives the story.")
    resolution = st.text_input("Story Climax and Conclusion:", help="Explain how the plot reaches its peak and resolves.")
    moral = st.text_input("Moral of the story:")
    if st.button("Generate Custom Story"):
        generate_story(story_type, main_character, setting, conflict, resolution, moral, length_minutes, include_illustrations, include_audio, selected_language)

# Tab 3: Display Previously Saved Stories
with tab3:
    st.write("(Story Archive)")
    previous_stories = load_stories_from_json()
    if previous_stories:
        for story in previous_stories:
            with st.expander(f"{story['story_type']} - {story['main_character']}"):
                # Ensure each paragraph of saved stories is wrapped in dynamic font
                for paragraph in story["text"].split('\n'):
                    st.markdown(f'<div class="dynamic-font">{paragraph}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Genre: {story["story_type"]}, Main Character: {story["main_character"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Setting: {story["setting"]}, Conflict: {story["conflict"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dynamic-font">Resolution: {story["resolution"]}, Moral: {story["moral"]}</div>', unsafe_allow_html=True)
    else:
        st.write("No previous stories found.")
