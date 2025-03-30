from flask import Flask, request, jsonify
import sys, os

# Ensure the script can import utility functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import fetch_figma_json, fetch_pdf_text
from agents.test_generation.test_llm import generate_test_cases
from agents.test_scenerio_script.sel_script import generate_selenium_js,scrape_website

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/process', methods=['POST'])
def process_data():
    """Processes Figma JSON and Requirements to generate test cases."""
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


@app.route('/generate_test_script', methods=['POST'])
def generate_test_script():
    data = request.json
    
    test_cases = data.get("test_cases")
    website_url = data.get("website_url")
    
    if not test_cases or not website_url:
        return jsonify({"error": "Provide both test cases and a website URL"}), 400
    
    try:
        # Scrape website data
        website_data = scrape_website(website_url)
        
        # Generate Selenium JS script
        selenium_script = generate_selenium_js(test_cases, website_data)
        
        return jsonify({"message": "Test script generated successfully", "selenium_script": selenium_script})
    except Exception as e:
        return jsonify({"error": f"Test script generation failed: {str(e)}"}), 500

@app.route('/generate_from_figma', methods=['POST'])
def generate_from_figma():
    """Processes Figma image and requirements URL to generate test cases."""
    if 'figma_image' not in request.files:
        return jsonify({"error": "Figma image is required."}), 400
    
    figma_image = request.files['figma_image']
    requirements_url = request.form.get("requirements_url", "")
    
    if not requirements_url:
        return jsonify({"error": "Requirements URL is required."}), 400
    
    try:
        figma_data = process_figma_image(figma_image)
        requirements_text = fetch_pdf_text(requests.get(requirements_url).content)
        test_cases = generate_test_cases(figma_data, requirements_text)
        return jsonify({"message": "Test cases generated successfully", "test_cases": test_cases})
    except Exception as e:
        return jsonify({"error": f"Test case generation failed: {str(e)}"}), 500


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
