from flask import Flask, request, jsonify
import sys
import os
import tiktoken  # Import tokenizing library
import orjson  # Add this at the top of the file


# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.utils import fetch_figma_json, fetch_pdf_text, fetch_website_data
from agents.test_case_generation.supervisor_agent import full_pipeline

app = Flask(__name__)

# Store test cases & failed tests in memory (can be replaced with DB)
test_cases = None
failed_tests = None

# Define token limit (adjust based on model constraints)
TOKEN_LIMIT = 2000  # Example: Set to match your LLM's context size

def count_tokens(text):
    """Returns the number of tokens in a string using tiktoken."""
    encoding = tiktoken.get_encoding("cl100k_base")  # Use appropriate encoding
    return len(encoding.encode(text))

def truncate_to_limit(text, limit):
    """Trims text to fit within the token limit."""
    tokens = count_tokens(text)
    if tokens > limit:
        print(f"Truncating text from {tokens} tokens to {limit} tokens.")  # Debugging
        encoding = tiktoken.get_encoding("cl100k_base")
        truncated_text = encoding.decode(encoding.encode(text)[:limit])
        return truncated_text
    return text

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
    if figma_json is None or not isinstance(figma_json, dict):
        return jsonify({"error": "Invalid or missing 'figma_url'"}), 400

    # Validate figma_json structure
    if not all(key in figma_json for key in ['Layout_agent', 'Usability_agent']):
        return jsonify({"error": "Invalid figma_json structure"}), 400

    if not requirements_content or (isinstance(requirements_content, dict) and 'error' in requirements_content):
        error_msg = requirements_content.get('error', 'Invalid PDF content')
        return jsonify({"error": "Invalid requirement PDF", "details": error_msg}), 400

    # Convert inputs to strings (if necessary)
    figma_json_str = orjson.dumps(figma_json).decode("utf-8") if isinstance(figma_json, dict) else str(figma_json)
    requirements_content_str = str(requirements_content) if isinstance(requirements_content, str) else ""

    # Apply token limits before passing to `full_pipeline`
    figma_json_str = truncate_to_limit(figma_json_str, TOKEN_LIMIT)
    requirements_content_str = truncate_to_limit(requirements_content_str, TOKEN_LIMIT)

    try:
        print("Passing to full_pipeline (After Truncation):")
        print("Figma JSON:", figma_json)
        print("Requirements Content (truncated):", requirements_content_str[:500])  # Debugging

        test_cases = full_pipeline(figma_json_str, requirements_content_str)
    except Exception as e:
        print("Exception in full_pipeline:", str(e))  # Debugging log
        return jsonify({"error": f"Failed to generate test cases: {str(e)}"}), 500

    return jsonify({
        "message": "UI/UX test cases generated successfully. Now provide 'website_url' to run tests.",
        "test_cases": test_cases
    })

if __name__ == '__main__':
    app.run(debug=True)
