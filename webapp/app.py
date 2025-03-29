import streamlit as st
import requests

# Flask API URL (Update if running on a different host)
API_URL = "http://127.0.0.1:5000/process_figma"

# Streamlit UI
st.title("Figma Test Plan Generator")

# Input fields
figma_url = st.text_input("Enter Figma File URL", placeholder="https://www.figma.com/file/xyz123/design")
requirements = st.text_area("Enter Testing Requirements (one per line)", placeholder="Check text consistency\nValidate button interactions")

# Convert text area input to list
requirements_list = [req.strip() for req in requirements.split("\n") if req.strip()]

# Submit button
if st.button("Generate Test Plan"):
    if figma_url:
        # Prepare payload
        payload = {
            "figma_url": figma_url,
            "requirements": requirements_list
        }
        
        # Send data to Flask API
        response = requests.post(API_URL, json=payload)
        
        # Display API response
        if response.status_code == 200:
            st.success("Test Plan Generated Successfully!")
            st.json(response.json())
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
    else:
        st.error("Please enter a valid Figma URL.")
