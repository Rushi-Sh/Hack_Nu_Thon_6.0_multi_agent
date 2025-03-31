from flask import Flask, request, jsonify
import sys, os
from PIL import Image
import io
import requests
# Ensure the script can import utility functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import fetch_figma_json, fetch_pdf_text
from agents.test_generation.test_llm import generate_test_cases
from agents.test_generation.test_manual import generate_manual_test_cases
from agents.test_scenerio_script.sel_script import generate_selenium_js,scrape_website
from agents.figma_image.image_test import extract_ui_elements_from_image,generate_image_test_cases
from agents.general_chatbot.chatty import generate_chat_response

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/process', methods=['POST'])
def process_data():

    data = request.json if request.is_json else request.form.to_dict()

    # Extract Figma JSON
    figma_json = fetch_figma_json(data.get("figma_url")) if data.get("figma_url") else None

    # Extract Requirements Text (from PDF or direct input)
    requirements_text = None
    if "requirement_pdf" in request.files:
        requirements_text = fetch_pdf_text(request.files["requirement_pdf"].read())
    elif "requirements_text" in data:
        requirements_text = data["requirements_text"].strip()

    # Validate inputs
    if not figma_json and not requirements_text:
        return jsonify({"error": "Provide at least Figma JSON or requirements text"}), 400

    # Generate test cases
    try:
        test_cases = generate_test_cases(figma_json, requirements_text)
        return jsonify({"message": "Test cases generated successfully", "test_cases": test_cases})
    except Exception as e:
        return jsonify({"error": f"Test generation failed: {str(e)}"}), 500

@app.route('/manual_input', methods=['POST'])
def manual_input():

    data = request.json if request.is_json else request.form.to_dict()

    # Extract UI and requirements descriptions
    ui_desc = data.get("ui_description", "").strip()
    requirement_desc = data.get("requirement_description", "").strip()

    # Validate inputs
    if not ui_desc and not requirement_desc:
        return jsonify({"error": "Provide at least UI description or requirements description"}), 400

    # Generate test cases
    try:
        test_cases = generate_manual_test_cases(ui_desc, requirement_desc)
        return jsonify({"message": "Test cases generated successfully", "test_cases": test_cases})
    except Exception as e:
        return jsonify({"error": f"Test generation failed: {str(e)}"}), 500


@app.route('/generate_test_script', methods=['POST'])
def generate_test_script():
    data = request.json if request.is_json else request.form.to_dict()
    
    test_cases = data.get("test_cases")
    website_url = data.get("website_url")
    
    if not test_cases or not website_url:
        return jsonify({"error": "Provide both test cases and a website URL"}), 400
    
    try:
        # Scrape website data
        website_data = scrape_website(website_url)
        
        # Generate Selenium JS script
        selenium_script = generate_selenium_js(test_cases, website_data)
        
        # Prepare the data to send to the external API
        test_data = {
            "website_url": website_url,
            "selenium_script": selenium_script
        }
        
        # Send the Selenium script and website URL to another API to get the test results
        test_results_url = "https://your-test-results-api-url.com"  # Replace with your actual API URL
        response = requests.post(test_results_url, json=test_data)
        
        if response.status_code == 200:
            test_results = response.json()  # Assuming the API returns a JSON response with the test results
            return jsonify({"message": "Test script generated and test results received successfully", 
                            "selenium_script": selenium_script, 
                            "test_results": test_results})
        else:
            return jsonify({"error": "Failed to get test results from external API", 
                            "status_code": response.status_code, 
                            "response": response.text}), 500
        
    except Exception as e:
        return jsonify({"error": f"Test script generation or API call failed: {str(e)}"}), 500

@app.route('/generate_from_figma', methods=['POST'])
def generate_from_figma():

    if 'figma_image' not in request.files:
        return jsonify({"error": "Figma image is required."}), 400
    
    if 'requirement_pdf' not in request.files:
        return jsonify({"error": "Requirements PDF is required."}), 400
    
    try:
        # Read Figma image
        figma_image = request.files['figma_image']
        image_bytes = figma_image.read()
        processed_image = Image.open(io.BytesIO(image_bytes))
        
        # Read and extract text from the PDF
        requirement_pdf = request.files['requirement_pdf'].read()
        requirements_text = fetch_pdf_text(requirement_pdf)
        
        # Generate test cases
        test_cases = generate_test_cases(processed_image, requirements_text)
        
        return jsonify({"message": "Test cases generated successfully", "test_cases": test_cases})
    
    except Exception as e:
        return jsonify({"error": f"Test case generation failed: {str(e)}"}), 500


@app.route('/chatbot', methods=['POST'])
def chatbot():

    data = request.json if request.is_json else request.form.to_dict()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Please provide a message"}), 400

    try:
        bot_response = generate_chat_response(user_message)
        return jsonify({"message": "Response generated successfully", "response": bot_response})
    except Exception as e:
        return jsonify({"error": f"Chatbot response failed: {str(e)}"}), 500


@app.route('/test_suggestions', methods=['POST'])
def test_suggestions():
    """Handle request to generate test case suggestions."""
    data = request.json if request.is_json else request.form.to_dict()
    test_case_id = data.get("id")

    if not test_case_id:
        return jsonify({"error": "Test case ID is required"}), 400

    suggestions = generate_suggestions_for_test_case(test_case_id)

    if "error" in suggestions:
        return jsonify(suggestions), 400

    return jsonify({"message": "Test case suggestions generated successfully", "suggestions": suggestions["suggestions"]})


@app.route('/suggest_updates', methods=['POST'])
def suggest_updates():
    """Suggests updates to test scenarios based on test results."""
    data = request.json
    test_results = data.get("test_results")

    if not test_results:
        return jsonify({"error": "Provide test results"}), 400

    try:
        updated_scenarios = suggest_test_updates(test_results)
        return jsonify({"message": "Test scenarios updated successfully", "updated_test_cases": updated_scenarios})
    except Exception as e:
        return jsonify({"error": f"Update suggestion failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
