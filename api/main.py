from flask import Flask, request, jsonify
import sys, os

# Ensure the script can import utility functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import fetch_figma_json, fetch_pdf_text
from agents.test_generation.test_llm import generate_test_cases

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
