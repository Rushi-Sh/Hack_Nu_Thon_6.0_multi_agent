import os
import re
import google.generativeai as genai
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-pro")


# Function to scrape the website
def scrape_website(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=15000, wait_until="networkidle")

        # Extract interactive elements
        buttons = [btn.inner_text() for btn in page.locator("button").all()]
        inputs = [inp.get_attribute("name") for inp in page.locator("input").all() if inp.get_attribute("name")]
        forms = [form.get_attribute("action") for form in page.locator("form").all() if form.get_attribute("action")]
        links = [a.get_attribute("href") for a in page.locator("a").all() if a.get_attribute("href")]

        browser.close()

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


# Function to generate Selenium JS script using Gemini API (Without LangChain)
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

    # Direct Gemini API Call
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

    # Scrape website data
    website_data = scrape_website(website_url)

    # Generate Selenium JS script
    selenium_script = generate_selenium_js(test_cases, website_data)

    if selenium_script:
        # Save the script to a file
        with open("selenium_test.js", "w") as file:
            file.write(selenium_script)

        print("\n✅ Selenium Test Script Generated Successfully! Saved as 'selenium_test.js'")
    else:
        print("\n❌ Failed to generate a valid Selenium script.")
