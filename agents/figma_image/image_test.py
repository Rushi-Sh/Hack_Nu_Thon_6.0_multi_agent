import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import io

# Load API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
gemini_model = genai.GenerativeModel("gemini-1.5-flash")


def extract_ui_elements_from_image(image_path):
    """Extract UI elements from an image using Gemini API."""
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    
    image = Image.open(io.BytesIO(image_data))
    prompt = "Extract UI elements from this image."

    response = gemini_model.generate_content([prompt, image])

    return response.text if response else None


def generate_test_cases(ui_elements, requirements):
    """Generate structured test cases based on extracted UI elements and requirements."""
    prompt = f"""
    Generate structured test cases based on the following inputs:

    **Image UI Components Data:**  
    {ui_elements}

    **Requirements Document:**  
    {requirements}

    **Focus Areas:**  
    - Functional testing  
    - Layout and UI validation  
    - Accessibility checks  
    - Edge cases  
    - Error handling  

    **Return the response in valid JSON format only, structured as follows:**  

    {{
        "summary": "Brief description of the test scenario",
        "priority": "P1 or P2 or P3",
        "tags": ["Tag1", "Tag2"],
        "test_cases": [
            {{
                "step": "Action to be performed",
                "expected_result": "Expected outcome"
            }},
            {{
                "step": "Next action",
                "expected_result": "Next expected outcome"
            }}
        ]
    }}

    Ensure the response is strictly valid JSON with no extra text or explanations.
    """

    response = gemini_model.generate_content(prompt)

    try:
        return json.loads(response.text) if response else None
    except json.JSONDecodeError:
        print("❌ Failed to parse response as JSON.")
        return None


# Main Execution
if __name__ == "__main__":
    image_path = "LandingPage.png"  # Replace with actual UI image file
    requirements = "The UI should support user login, password validation, form submission, and error handling."

    # Extract UI elements
    ui_elements = extract_ui_elements_from_image(image_path)

    print(ui_elements)  # Print the extracted inf

    if ui_elements:
        # Generate test cases
        test_cases = generate_test_cases(ui_elements, requirements)

        if test_cases:
            # Save to a JSON file
            with open("test_cases.json", "w") as file:
                json.dump(test_cases, file, indent=4)
            print("✅ Test cases generated successfully! Saved as 'test_cases.json'")
        else:
            print("❌ Failed to generate test cases.")
    else:
        print("❌ Failed to extract UI elements from image.")
