import streamlit as st
import requests
import json
from menu import menu  # Import menu module

# API URLs
API_URL_PROCESS = "http://127.0.0.1:5000/process"
API_URL_GENERATE_FROM_FIGMA = "http://127.0.0.1:5000/generate_from_figma"
API_URL_MANUAL_INPUT = "http://127.0.0.1:5000/manual_input"

# Display menu and get selected option
option = menu()

if option == "Home":
    st.title("Welcome to the Test Case Generator")
    st.write("""
    This application helps you generate automated test cases from Figma designs and requirement documents.
    
    **Features:**
    - Generate test cases from a Figma URL
    - Generate test cases from uploaded Figma images
    - Generate test cases manually from UI descriptions
    - Save test cases in JSON format
    - Generate Selenium test scripts from test cases
    
    Select an option from the sidebar to get started!
    """)

elif option == "Generate Test Cases":
    st.title("Test Case Generator")
    
    input_method = st.radio("Select Input Method:", ["Figma URL", "Figma Image Upload"])

    if input_method == "Figma URL":
        figma_url = st.text_input("Enter Figma File URL", placeholder="https://www.figma.com/file/xyz123/design")
        requirements_text = st.text_area("Enter Requirements Text")
        
        if st.button("Generate Test Cases"):
            if figma_url or requirements_text:
                payload = {"figma_url": figma_url or None, "requirements_text": requirements_text or None}
                try:
                    response = requests.post(API_URL_PROCESS, json=payload)
                    if response.status_code == 200:
                        st.success("Test Cases Generated Successfully!")
                        st.json(response.json())

                        with open("test_cases.json", "w") as file:
                            json.dump(response.json(), file)
                        st.success("Test Cases Saved to 'test_cases.json'")
                    else:
                        st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error: Unable to connect to API. {str(e)}")
            else:
                st.warning("Please provide either a Figma URL or requirements text")
    
    elif input_method == "Figma Image Upload":
        figma_image = st.file_uploader("Upload Figma Image", type=["png", "jpg", "jpeg"])
        requirements_pdf = st.file_uploader("Upload Requirements PDF", type=["pdf"])
        
        if st.button("Generate Test Cases"):
            if figma_image and requirements_pdf:
                try:
                    files = {"figma_image": (figma_image.name, figma_image, figma_image.type),
                             "requirement_pdf": (requirements_pdf.name, requirements_pdf, "application/pdf")}
                    response = requests.post(API_URL_GENERATE_FROM_FIGMA, files=files)
                    if response.status_code == 200:
                        st.success("Test Cases Generated Successfully!")
                        st.json(response.json())
                        with open("test_cases.json", "w") as file:
                            json.dump(response.json(), file)
                        st.success("Test Cases Saved to 'test_cases.json'")
                    else:
                        st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error: Unable to connect to API. {str(e)}")
            else:
                st.warning("Please upload both a Figma image and a requirements PDF")

elif option == "Test Manual Input":
    st.title("Test Manual Input")
    
    ui_description = st.text_area("Enter UI Description")
    requirements_text = st.text_area("Enter Requirements Text")
    
    if st.button("Generate Test Cases"):
        if ui_description or requirements_text:
            payload = {"ui_description": ui_description or None, "requirements_description": requirements_text or None}
            try:
                response = requests.post(API_URL_MANUAL_INPUT, json=payload)
                if response.status_code == 200:
                    st.success("Test Cases Generated Successfully!")
                    st.json(response.json())
                    with open("test_cases_manual.json", "w") as file:
                        json.dump(response.json(), file)
                    st.success("Test Cases Saved to 'test_cases_manual.json'")
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error: Unable to connect to API. {str(e)}")
        else:
            st.warning("Please provide UI description or requirements text")

elif option == "Generate Test Script":
    st.title("Generate Test Script")
    uploaded_test_cases = st.file_uploader("Upload Test Cases JSON File", type=["json"])
    website_url = st.text_input("Enter Website URL for Test Script", placeholder="https://example.com")

    if st.button("Generate Test Script"):
        if uploaded_test_cases and website_url:
            test_cases_data = json.load(uploaded_test_cases)
            test_script_payload = {"website_url": website_url, "test_cases": test_cases_data}
            try:
                response = requests.post(API_URL_PROCESS, json=test_script_payload)
                if response.status_code == 200:
                    st.success("Test Script Generated Successfully!")
                    st.json(response.json())
                    with open("selenium_test.js", "w") as file:
                        file.write(response.json()["script"])
                    st.success("Test Script Saved to 'selenium_test.js'")
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error: Unable to connect to API. {str(e)}")
        else:
            st.error("Please provide both test cases JSON file and Website URL.")
