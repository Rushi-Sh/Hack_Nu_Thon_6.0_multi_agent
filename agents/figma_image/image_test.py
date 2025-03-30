import os
import json
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv
from PIL import Image
import io

# Load API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize LangChain LLM with Gemini 1.5 Flash
llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)


def extract_ui_elements_from_image(image_path):
    # Read image file in binary mode
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    
    # Convert bytes to PIL Image
    image = Image.open(io.BytesIO(image_data))

    # Define the prompt
    prompt = "Extract UI elements from this image."

    # Initialize the Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Generate content with the image in the correct format
    response = model.generate_content([prompt, image])

    return response


def generate_test_cases(ui_elements, requirements):
    # Define the prompt
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

    # Convert GenerateContentResponse objects to serializable format
    serializable_ui_elements = []
    
    if isinstance(ui_elements, genai.types.GenerateContentResponse):
        response_dict = {
            'text': ui_elements.text,
            'candidates': [
                {
                    'content': candidate.content.parts[0].text if candidate.content.parts else None,
                    'finish_reason': candidate.finish_reason
                }
                for candidate in ui_elements.candidates
            ]
        }
        serializable_ui_elements.append(response_dict)
    elif isinstance(ui_elements, (list, tuple)):
        for element in ui_elements:
            if isinstance(element, genai.types.GenerateContentResponse):
                response_dict = {
                    'text': element.text,
                    'candidates': [
                        {
                            'content': candidate.content.parts[0].text if candidate.content.parts else None,
                            'finish_reason': candidate.finish_reason
                        }
                        for candidate in element.candidates
                    ]
                }
                serializable_ui_elements.append(response_dict)
            else:
                serializable_ui_elements.append(element)

    return json.dumps(serializable_ui_elements, indent=2)
    

# Main Execution
if __name__ == "__main__":
    image_path = "LandingPage.png"  # Replace with actual UI image file
    requirements = "The UI should support user login, password validation, form submission, and error handling."
    
    # Extract UI elements
    ui_elements = extract_ui_elements_from_image(image_path)
    
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