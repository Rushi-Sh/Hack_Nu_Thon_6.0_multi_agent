import streamlit as st
import requests
import PyPDF2

# Flask API URL (Update if running on a different host)
API_URL = "http://127.0.0.1:5000/process"

# Streamlit UI
st.title("Automated Test Plan Generator")

# Input field for Figma URL
figma_url = st.text_input("Enter Figma File URL", placeholder="https://www.figma.com/file/xyz123/design")

# Input field for Website URL
# website_url = st.text_input("Enter Website URL for Testing", placeholder="https://example.com")

# File uploader for PDF requirements
uploaded_file = st.file_uploader("Upload PDF with Testing Requirements", type=["pdf"])

requirements_list = []

if uploaded_file:
    # Read PDF content
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            requirements_list.extend([line.strip() for line in text.split("\n") if line.strip()])

# Display extracted requirements
if requirements_list:
    st.write("### Extracted Testing Requirements:")
    for req in requirements_list:
        st.write(f"- {req}")

# Submit button
if st.button("Generate Test Plan"):
    if figma_url  or requirements_list:
        # Prepare payload based on available data
        payload = {}
        if figma_url:
            payload["figma_url"] = figma_url
        # if website_url:
        #     payload["website_url"] = website_url
        
        # Send data to Flask API
        files = {}
        if uploaded_file:
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            files = {"requirement_pdf": uploaded_file}
            
        # Send request with JSON payload and/or files
        if files:
            # Don't use json parameter when sending files
            # Instead, include the JSON data as part of the form data
            response = requests.post(API_URL, data=payload, files=files)
        else:
            response = requests.post(API_URL, json=payload)
        
        # Display API response
        if response.status_code == 200:
            try:
                st.success("Test Plan Generated Successfully!")
                st.json(response.json())
            except requests.exceptions.JSONDecodeError:
                st.error("Error: Invalid response from API. The server returned an invalid JSON response.")
        else:
            try:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")
            except requests.exceptions.JSONDecodeError:
                st.error(f"Error: Server returned status code {response.status_code} with invalid JSON response.")
    else:
        st.error("Please provide at least one of the following: Figma URL or upload a PDF with testing requirements.")
