import streamlit as st
import requests
import io
from PIL import Image
import google.generativeai as genai
import textwrap
from streamlit import markdown as st_markdown

# Constants
HF_API_TOKEN = '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'
HF_API_URL = "https://api-inference.huggingface.co/models/lambdalabs/sd-pokemon-diffusers"
HF_HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

GOOGLE_API_KEY='AIzaSyDM3sIaO5riFJ1_b85X4HLY5-KWZNwYoOQ'
genai.configure(api_key=GOOGLE_API_KEY)
MODEL = genai.GenerativeModel('gemini-pro-vision')

# Function to query Hugging Face API for image generation
def query_hf(payload):
    response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload)
    return response.content

# Function to generate Pokémon data
def get_pokemon_data(description):
    # Generate image
    image_bytes = query_hf({"inputs": description})
    image = Image.open(io.BytesIO(image_bytes))
    image_path = "generated_image.jpg"
    image.save(image_path, "JPEG", quality=100)
    
    # Generate content
    response = MODEL.generate_content([f"Generate a unique and creative name for this Pokémon. Create a detailed description for a new Pokémon named based on the image.", image], stream=True)
    response.resolve()
    pokemon_description = response.text

    return pokemon_description, image_path

# Streamlit app layout
st.title("Pokédex")

# Input text box
initial_text = st.text_input("Enter some initial text:")

# Generate button
if st.button("Generate"):
    if initial_text:
        # Get Pokémon data
        pokemon_description, pokemon_image_path = get_pokemon_data(initial_text)

        # Display Pokémon description
        st_markdown(st.markdown(f"Generated Pokémon: {pokemon_description}"))

        # Load and display Pokémon image from local path
        try:
            img = Image.open(pokemon_image_path)
            st.image(img, caption=pokemon_description)
        except FileNotFoundError:
            st.error("Image file not found. Please check the path.")
    else:
        st.warning("Please enter some text before generating a Pokémon.")
