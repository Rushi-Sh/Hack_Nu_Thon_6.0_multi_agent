import os
import re
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-pro")


# Function to scrape website using BeautifulSoup
def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP errors
    except requests.RequestException as e:
        print(f"⚠️ Failed to fetch website: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    buttons = [btn.get_text(strip=True) for btn in soup.find_all("button")]
    inputs = [inp.get("name") for inp in soup.find_all("input") if inp.get("name")]
    forms = [form.get("action") for form in soup.find_all("form") if form.get("action")]
    links = [a.get("href") for a in soup.find_all("a") if a.get("href")]

    return {
        "buttons": buttons,
        "input_fields": inputs,
        "forms": forms,
        "links": links
    }


# Function to extract JavaScript code using regex
def extract_js_code(response_text):
    match = re.search(r"```javascript(.*?)```", response_text, re.DOTALL)
    return match.group(1).strip() if match else None


# Function to generate Selenium JS script using Gemini API
def generate_selenium_js(test_cases, website_data):
    prompt = f"""
    Generate a Selenium JavaScript script to automate testing for the following test cases:

    Test Cases:
    {test_cases}

    Website UI Elements:
    {website_data}

    Use Selenium WebDriver in JavaScript with Mocha framework for assertions. Make sure to:
    - Navigate to the URL
    - Interact with buttons, input fields, and forms
    - Verify expected test outcomes

    Return only the code inside a JavaScript code block (```javascript ... ```).
    """

    response = model.generate_content(prompt)

    if response and response.text:
        selenium_script = extract_js_code(response.text)
    else:
        selenium_script = None

    if not selenium_script:
        print("⚠️ No JavaScript code found in the response.")
        return None

    return selenium_script


# Main Execution
if __name__ == "__main__":
    website_url = "https://urbansnap.vercel.app/"  # Replace with target website
    test_cases = [
        {"test_case": "Verify login button is clickable"},
        {"test_case": "Fill the login form with valid credentials and submit"},
        {"test_case": "Ensure the logout button is visible after login"}
    ]

    # Scrape website data using BeautifulSoup
    website_data = scrape_website(website_url)

    if website_data:
        # Generate Selenium JS script
        selenium_script = generate_selenium_js(test_cases, website_data)

        if selenium_script:
            with open("selenium_test.js", "w") as file:
                file.write(selenium_script)

            print("\n✅ Selenium Test Script Generated Successfully! Saved as 'selenium_test.js'")
        else:
            print("\n❌ Failed to generate a valid Selenium script.")
    else:
        print("\n❌ Failed to scrape website data.")
