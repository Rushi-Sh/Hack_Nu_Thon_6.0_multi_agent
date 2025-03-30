from flask import Flask, request, jsonify
import sys
import os

# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.utils import fetch_figma_json, fetch_pdf_text, fetch_website_data
from agents.test_case_generation.supervisor_agent import full_pipeline

app = Flask(__name__)

# Store test cases & failed tests in memory (can be replaced with DB)
test_cases = None
failed_tests = None

@app.route('/process', methods=['POST'])
def process_data():
    global test_cases, failed_tests
    failed_tests = None  # Reset failed tests

    data = request.form if request.form else request.json if request.is_json else {}

    figma_json, requirements_content = None, None

    # Validate and fetch Figma data
    figma_url = data.get("figma_url")
    if figma_url:
        figma_json = fetch_figma_json(figma_url)
        if isinstance(figma_json, dict) and 'error' in figma_json:
            return jsonify({"error": figma_json['error']}), 400
    
    # Validate and fetch requirements from PDF
    if "requirement_pdf" in request.files:
        pdf_bytes = request.files["requirement_pdf"].read()
        requirements_content = fetch_pdf_text(pdf_bytes)

    # Ensure both inputs are provided
    if figma_json is None:
        return jsonify({"error": "Invalid or missing 'figma_url'"}), 400



    
    if not requirements_content or (isinstance(requirements_content, dict) and 'error' in requirements_content):
        error_msg = requirements_content.get('error', 'Invalid PDF content')
        return jsonify({"error": "Invalid requirement PDF", "details": error_msg}), 400

    try:
        print("Passing to full_pipeline:")
        print("Figma JSON:", figma_json)
        print("Requirements Content:", requirements_content)
        test_cases = full_pipeline(figma_json, requirements_content)
    except Exception as e:
        print("Exception in full_pipeline:", str(e))  # Debugging log
        return jsonify({"error": f"Failed to generate test cases: {str(e)}"}), 500

    return jsonify({
        "message": "UI/UX test cases generated successfully. Now provide 'website_url' to run tests.",
        "test_cases": test_cases
    })

if __name__ == '__main__':
    app.run(debug=True)