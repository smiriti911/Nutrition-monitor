import streamlit as st
from dotenv import load_dotenv, find_dotenv
import os
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components

# Load environment variables from the .env file
load_dotenv(find_dotenv())

# Configure Streamlit page settings
st.set_page_config(page_title="Nutrition Monitor", page_icon="🥕", layout="wide")

# Configure Google Generative AI library with an API key from environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load the external CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Define a function to handle the response from Google Gemini API
def get_gemini_response(input, image):
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    try:
        response = model.generate_content([input, image[0]])
        return response.text
    except Exception as e:
        st.error(f"Error communicating with the Gemini API: {str(e)}")
        return "An error occurred while analyzing the image."

# Define a function to set up image uploading and handle the image data
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
        return image_parts
    else:
        raise FileNotFoundError("No image uploaded")

# Sidebar configuration for navigation and file upload
st.sidebar.title("Navigation")
st.sidebar.header("Upload Section")
uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Main header of the application
st.header("Nutrition Monitor")

# Check if an image is uploaded and display it
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True, clamp=True)

# Create a button for triggering the food analysis
submit = st.button("Analyze this Food")

# Set the prompt for the AI model
input_prompt = """
You are an expert nutritionist analyzing the food items in the image.
Start by determining if the image contains food items. 
If the image does not contain any food items, 
clearly state "No food items detected in the image." 
and do not provide any calorie information. 
If food items are detected, 
start by naming the meal based on the image, 
identify and list every ingredient you can find in the image, 
and then estimate the total calories for each ingredient. 
Summarize the total calories based on the identified ingredients. 
Follow the format below:

If no food items are detected:
No food items detected in the image.

If food items are detected:
Meal Name: [Name of the meal]

1. Ingredient 1 - estimated calories
2. Ingredient 2 - estimated calories
----
Total estimated calories: X

Finally, mention whether the food is healthy or not, 
and provide the percentage split of protein, carbs, and fats in the food item. 
Also, mention the total fiber content in the food item and any other important details.

Note: Always identify ingredients and provide an estimated calorie count, 
even if some details are uncertain.
"""

# Action to take when the 'Analyze this Food' button is clicked
if submit:
    with st.spinner("Processing..."):  # Show a processing spinner while processing
        try:
            image_data = input_image_setup(uploaded_file)  # Prepare the image data
            response = get_gemini_response(input_prompt, image_data)  # Get the response from the AI model
            st.success("Done!")  # Indicate processing is complete
            st.subheader("Food Analysis")
            st.write(response)  # Display the response from the AI model
        except FileNotFoundError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

# Footer
st.markdown("<div class='footer'>🫛Track Your Plate, Transform Your Health🫛</div>", unsafe_allow_html=True)
