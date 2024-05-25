import streamlit as st
import requests
import io
from PIL import Image
from google.generativeai import generativeai as genai
import google.ai.generativelanguage as glm
import textwrap

# Constants for Hugging Face API
API_TOKEN = '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'
API_URL = "https://api-inference.huggingface.co/models/lambdalabs/sd-pokemon-diffusers"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Configure Google Generative AI
GOOGLE_API_KEY = 'AIzaSyDM3sIaO5riFJ1_b85X4HLY5-KWZNwYoOQ'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro-vision')

# Function to query Hugging Face API for image generation
def query_huggingface(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        st.error(f"Error: {response.status_code}, {response.text}")
        return None
    return response.content

# Function to generate Pokémon data
def get_pokemon_data(initial_text):
    # Generate image
    image_bytes = query_huggingface({"inputs": initial_text})
    if image_bytes is None:
        return None, None, None

    # Save the response content to a file for inspection (debugging step)
    with open("response_content.bin", "wb") as f:
        f.write(image_bytes)

    try:
        # Attempt to open the image using PIL
        image = Image.open(io.BytesIO(image_bytes))
        image_path = "generated_image.jpg"
        image.save(image_path, "JPEG", quality=100)
    except Exception as e:
        st.error(f"Failed to generate image: {e}")
        return None, None, None

    # Generate text description
    try:
        response = model.generate_content([
            f"Generate a unique and creative name for this Pokémon. "
            f"Create a detailed description for a new Pokémon named {initial_text}. "
            f"Include its type, abilities, and a brief backstory.",
            image
        ], stream=True)
        response.resolve()
        description = response.text
    except Exception as e:
        st.error(f"Failed to generate description: {e}")
        return None, image_path, None

    return initial_text, image_path, description

# Streamlit app
st.title("Pokédex")

# Input text box
initial_text = st.text_input("Enter some initial text:")

# Generate button
if st.button("Generate"):
    if initial_text:
        # Get Pokémon data
        pokemon_name, pokemon_image_path, pokemon_description = get_pokemon_data(initial_text)

        if pokemon_name and pokemon_image_path and pokemon_description:
            # Display Pokémon name
            st.write(f"Generated Pokémon: {pokemon_name}")

            # Load and display Pokémon image from local path
            try:
                img = Image.open(pokemon_image_path)
                st.image(img, caption=pokemon_name)
            except FileNotFoundError:
                st.error("Image file not found. Please check the path.")

            # Display Pokémon description
            st.write(pokemon_description)
        else:
            st.error("Failed to generate Pokémon data.")
    else:
        st.warning("Please enter some text before generating a Pokémon.")
