from flask import Flask, request, jsonify
import sys
import os

# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.utils import fetch_figma_json, fetch_pdf_text, fetch_website_data
from agents.test_case_generation.supervisor_agent import full_pipeline
# from test_engine import run_tests
# from code_fixer import suggest_code_updates
# from test_case_generator import generate_test_cases

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_data():
    """
    Processes input data from Figma, website URL, or requirement PDF
    and runs a full testing pipeline across UI/UX, frontend, and backend.
    """
    data = request.form if request.form else request.json if request.is_json else {}

    figma_json, website_content, requirements_content = None, None, None

    if "figma_url" in data:
        figma_json = fetch_figma_json(data.get("figma_url"))
    if "website_url" in data:
        website_content = fetch_website_data(data.get("website_url"))
    if "requirement_pdf" in request.files:
        pdf_bytes = request.files["requirement_pdf"].read()
        requirements_content = fetch_pdf_text(pdf_bytes)

    if not any([figma_json, website_content, requirements_content]):
        return jsonify({"error": "Invalid request. Provide at least one input: 'figma_url', 'website_url', or 'requirement_pdf'"}), 400

    # Run the full testing pipeline
    pipeline_results = full_pipeline(figma_json, website_content, requirements_content)

    return jsonify({"pipeline_results": pipeline_results})

if __name__ == '__main__':
    app.run(debug=True)
