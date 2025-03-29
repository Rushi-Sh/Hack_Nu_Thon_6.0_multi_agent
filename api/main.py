from flask import Flask, request, jsonify
from utils import fetch_figma_json  # Importing function from utils.py

app = Flask(__name__)

@app.route('/process_figma', methods=['POST'])
def get_figma_data():
    """
    API endpoint to fetch Figma JSON data.
    Expects JSON input: { "figma_url": "https://www.figma.com/file/xyz123/design" }
    """
    data = request.json
    figma_url = data.get("figma_url")

    if not figma_url:
        return jsonify({"error": "Missing figma_url parameter"}), 400

    response = fetch_figma_json(figma_url)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
