import streamlit as st
import requests
import json

# API URLs
API_URL_PROCESS = "http://127.0.0.1:5000/process"
API_URL_GENERATE_FROM_FIGMA = "http://127.0.0.1:5000/generate_from_figma"

# Streamlit UI
st.title("Test Case Generator Menu")

# Menu options
option = st.sidebar.selectbox(
    "Select Input Method",
    ("Figma URL", "Figma Image Upload")
)

if option == "Figma URL":
    # Figma URL input
    figma_url = st.text_input("Enter Figma File URL", placeholder="https://www.figma.com/file/xyz123/design")
    requirements_text = st.text_area("Enter Requirements Text")
    
    if st.button("Generate Test Cases"):
        if figma_url or requirements_text:
            payload = {
                "figma_url": figma_url if figma_url else None,
                "requirements_text": requirements_text if requirements_text else None
            }
            
            try:
                response = requests.post(API_URL_PROCESS, json=payload)
                if response.status_code == 200:
                    st.success("Test Cases Generated Successfully!")
                    st.json(response.json())
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error: Unable to connect to API. {str(e)}")
        else:
            st.warning("Please provide either a Figma URL or requirements text")

elif option == "Figma Image Upload":
    # Figma image upload
    figma_image = st.file_uploader("Upload Figma Image", type=["png", "jpg", "jpeg"])
    requirements_url = st.text_input("Enter Requirements URL", placeholder="https://example.com/requirements.pdf")
    
    if st.button("Generate Test Cases"):
        if figma_image and requirements_url:
            try:
                files = {"figma_image": figma_image}
                data = {"requirements_url": requirements_url}
                
                response = requests.post(API_URL_GENERATE_FROM_FIGMA, files=files, data=data)
                if response.status_code == 200:
                    st.success("Test Cases Generated Successfully!")
                    st.json(response.json())
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error: Unable to connect to API. {str(e)}")
        else:
            st.warning("Please upload a Figma image and provide a requirements URL")