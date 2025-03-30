import streamlit as st
import requests
import PyPDF2

# Flask API URLs
API_URL_PROCESS = "http://localhost:8501/process"
API_URL_GENERATE_SCRIPT = "http://localhost:8501/generate_test_script"

# Streamlit UI
st.title("Automated Test Plan Generator")

# Input field for Figma URL
figma_url = st.text_input("Enter Figma File URL", placeholder="https://www.figma.com/file/xyz123/design")

# File uploader for PDF requirements
uploaded_file = st.file_uploader("Upload PDF with Testing Requirements", type=["pdf"])

# Submit button for generating test plan
if st.button("Generate Test Plan"):
    if figma_url or uploaded_file:
        # Prepare payload
        payload = {}
        if figma_url:
            payload["figma_url"] = figma_url

        files = {}
        if uploaded_file:
            uploaded_file.seek(0)  # Reset file pointer
            files = {"requirement_pdf": uploaded_file}
        
        try:
            # Send request with JSON payload and/or files
            response = requests.post(API_URL_PROCESS, data=payload, files=files) if files else requests.post(API_URL_PROCESS, json=payload)

            # Handle API response
            if response.status_code == 200:
                try:
                    test_plan = response.json()
                    st.success("Test Plan Generated Successfully!")
                    st.json(test_plan)

                    # Ask for Website URL after generating the test plan
                    website_url = st.text_input("Enter Website URL for Test Script", placeholder="https://example.com")

                    if website_url:
                        # Send the test case along with website URL to generate test script
                        test_script_payload = {
                            "website_url": website_url,
                            "test_case": test_plan  # Assuming the API expects a "test_case" field
                        }

                        # Request to generate test script
                        script_response = requests.post(API_URL_GENERATE_SCRIPT, json=test_script_payload)

                        if script_response.status_code == 200:
                            st.success("Test Script Generated Successfully!")
                            st.json(script_response.json())
                        else:
                            st.error(f"Error: {script_response.json().get('error', 'Unknown error')}")
                    else:
                        st.error("Please provide a Website URL for test script generation.")
                except requests.exceptions.JSONDecodeError:
                    st.error("Error: Invalid response from API. The server returned an invalid JSON response.")
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")

        except requests.exceptions.RequestException as e:
            st.error(f"Error: Unable to connect to API. {str(e)}")

    else:
        st.error("Please provide either a Figma URL or upload a PDF with testing requirements.")
