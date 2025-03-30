import streamlit as st
import requests
import json
import os

# Flask API URLs
API_URL_PROCESS = "http://127.0.0.1:5000/process"
API_URL_GENERATE_SCRIPT = "http://127.0.0.1:5000/generate_test_script"

# JSON filename to save test cases
TEST_CASES_FILE = "generated_test_cases.json"

# Streamlit UI
st.title("Automated Test Plan Generator")

# Step 1: Input Figma URL or Upload PDF
figma_url = st.text_input("Enter Figma File URL", placeholder="https://www.figma.com/file/xyz123/design")
uploaded_file = st.file_uploader("Upload PDF with Testing Requirements", type=["pdf"])

# Step 2: Generate and Save Test Plan as JSON
if st.button("Generate Test Plan"):
    if figma_url or uploaded_file:
        payload = {"figma_url": figma_url} if figma_url else {}
        files = {"requirement_pdf": uploaded_file} if uploaded_file else {}

        try:
            response = requests.post(API_URL_PROCESS, data=payload, files=files) if files else requests.post(API_URL_PROCESS, json=payload)

            if response.status_code == 200:
                try:
                    test_plan = response.json()

                    # Save test cases as a JSON file
                    with open(TEST_CASES_FILE, "w") as f:
                        json.dump(test_plan, f, indent=4)

                    st.success("Test Plan Generated and Saved as JSON File!")
                    st.json(test_plan)
                    st.info(f"Saved file: `{TEST_CASES_FILE}`")

                except requests.exceptions.JSONDecodeError:
                    st.error("Error: Invalid response from API. The server returned an invalid JSON response.")
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")

        except requests.exceptions.RequestException as e:
            st.error(f"Error: Unable to connect to API. {str(e)}")

    else:
        st.warning("Please provide either a Figma URL or upload a PDF with testing requirements.")

# Step 3: Upload Test Cases JSON and Provide Website URL
st.subheader("Step 3: Generate Selenium Test Script")

uploaded_json_file = st.file_uploader("Upload Generated Test Cases JSON", type=["json"])
website_url = st.text_input("Enter Website URL for Test Script", placeholder="https://example.com")

if st.button("Generate Test Script"):
    if uploaded_json_file and website_url:
        try:
            # Load test cases from uploaded JSON file
            test_cases = json.load(uploaded_json_file)

            # Prepare request payload
            test_script_payload = {
                "website_url": website_url,
                "test_cases": test_cases
            }

            # Request to generate test script
            script_response = requests.post(API_URL_GENERATE_SCRIPT, json=test_script_payload)

            if script_response.status_code == 200:
                st.success("Test Script Generated Successfully!")
                st.json(script_response.json())
            else:
                st.error(f"Error: {script_response.json().get('error', 'Unknown error')}")

        except json.JSONDecodeError:
            st.error("Error: Uploaded file is not a valid JSON.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error: Unable to connect to API. {str(e)}")

    else:
        st.warning("Please upload a valid test cases JSON file and enter a Website URL.")
