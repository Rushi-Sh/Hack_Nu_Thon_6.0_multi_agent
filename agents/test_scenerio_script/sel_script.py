import os
import google.generativeai as genai
from langchain.llms import GoogleGenerativeAI
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize LangChain LLM with Gemini
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)

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

    Return the code in proper JavaScript format.
    """

    response = llm.predict(prompt)
    return response

# Main Execution
if __name__ == "__main__":
    website_url = "https://example.com"  # Replace with target website
    test_cases = [
        {"test_case": "Verify login button is clickable"},
        {"test_case": "Fill the login form with valid credentials and submit"},
        {"test_case": "Ensure the logout button is visible after login"}
    ]

    # Scrape website data
    website_data = scrape_website(website_url)

    # Generate Selenium JS script
    selenium_script = generate_selenium_js(test_cases, website_data)

    # Save the script to a file
    with open("selenium_test.js", "w") as file:
        file.write(selenium_script)

    print("\n✅ Selenium Test Script Generated Successfully! Saved as 'selenium_test.js'")
