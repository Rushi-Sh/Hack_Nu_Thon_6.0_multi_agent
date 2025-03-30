import os
import json
import google.generativeai as genai
import re
from dotenv import load_dotenv
from PIL import Image
import io

# Load API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
gemini_model = genai.GenerativeModel("gemini-1.5-flash")


def extract_json_from_text(response_text):
    """Extracts the first valid JSON structure from a text response using regex."""
    json_pattern = r"\{[\s\S]*\}"  # Match JSON structure
    match = re.search(json_pattern, response_text)

    if match:
        try:
            return json.loads(match.group(0))  # Convert extracted text to JSON
        except json.JSONDecodeError:
            print("❌ Extracted JSON is not valid.")
            return None
    else:
        print("❌ No JSON found in response.")
        return None


def extract_ui_elements_from_image(image_bytes):
    """Extract key UI elements from a Figma-generated image using Gemini API."""
    image = Image.open(io.BytesIO(image_bytes))  # Convert bytes to an image

    # Improved prompt for structured extraction
    prompt = """
    Analyze this UI design image (from Figma) and extract key UI components in **structured JSON format**.

    **Categories to extract:**
    - Navigation elements (headers, sidebars, menus)
    - Interactive elements (buttons, input fields, toggles, dropdowns)
    - Forms (login, signup, contact forms)
    - Key text elements (headings, labels)
    - Visual elements (cards, banners, sections)
    - Call-to-action buttons (e.g., "Sign Up", "Submit", "Buy Now")

    **Return ONLY valid JSON inside a code block** like this:
    ```json
    {
        "navigation": ["Header", "Sidebar"],
        "buttons": ["Login Button", "Signup Button"],
        "input_fields": ["Email", "Password"],
        "forms": ["Login Form"],
        "headings": ["Main Heading"],
        "visual_elements": ["Hero Banner"],
        "cta": ["Get Started"]
    }
    ```

    Do not include any explanations or extra text.
    """

    response = gemini_model.generate_content([prompt, image])

    if response:
        print("\n🔹 RAW RESPONSE FROM GEMINI:\n", response.text)  # Debugging log
        return extract_json_from_text(response.text)
    else:
        print("❌ No response from Gemini.")
        return None


def generate_image_test_cases(ui_elements, requirements):
    """Generate at least 30 structured test cases based on extracted UI elements and requirements."""
    prompt = f"""
    Based on the extracted UI elements and requirements, generate at least **30 structured test cases**.

    **Extracted UI Components:**  
    {json.dumps(ui_elements, indent=2)}

    **Requirements:**  
    {requirements}

    **Focus Areas:**  
    - Functional testing (buttons, input validation, form submission)  
    - Layout and UI validation (alignment, responsiveness)  
    - Accessibility checks (screen reader compatibility, color contrast)  
    - Edge cases (long text input, special characters)  
    - Error handling (invalid login, incorrect inputs)  

    **Return strictly JSON inside a code block** like this:
    ```
    ```json
    {{
        "summary": "Test cases for UI validation",
        "priority": "P1",
        "tags": ["UI", "Functional", "Accessibility"],
        "test_cases": [
            {{"step": "Click login button", "expected_result": "Redirects to login page"}},
            {{"step": "Enter valid credentials", "expected_result": "User logs in successfully"}},
            {{"step": "Enter incorrect password", "expected_result": "Error message appears"}},
            {{"step": "Submit empty login form", "expected_result": "Validation error is displayed"}},
            {{"step": "Resize browser window", "expected_result": "UI elements adjust correctly"}},
            {{"step": "Try submitting form without email", "expected_result": "Email field validation error"}},
            {{"step": "Navigate via keyboard", "expected_result": "Keyboard navigation works smoothly"}},
            {{"step": "Try login with special characters in password", "expected_result": "Password validation works"}},
            {{"step": "Check contrast ratio of text", "expected_result": "Meets accessibility standards"}}
        ]
    }}
    ```
    ```

    Ensure the JSON contains at least **30 test cases** across **various categories**.
    """

    response = gemini_model.generate_content(prompt)

    if response:
        print("\n🔹 RAW TEST CASE RESPONSE FROM GEMINI:\n", response.text)  # Debugging log
        return extract_json_from_text(response.text)
    else:
        print("❌ No response for test cases.")
        return None


# Main Execution
if __name__ == "__main__":
    image_path = "LandingPage.png"  # Replace with actual UI image file
    requirements = "The UI should support user login, password validation, form submission, and error handling."

    # Extract UI elements
    ui_elements = extract_ui_elements_from_image(image_path)

    if ui_elements:
        print("\n✅ Extracted UI Elements:\n", json.dumps(ui_elements, indent=2))  # Debugging output
        
        # Generate test cases
        test_cases = generate_image_test_cases(ui_elements, requirements)

        if test_cases:
            with open("test_cases.json", "w") as file:
                json.dump(test_cases, file, indent=4)
            print("✅ 30+ test cases generated successfully! Saved as 'test_cases.json'")
        else:
            print("❌ Failed to generate test cases.")
    else:
        print("❌ Failed to extract UI elements from image.")
