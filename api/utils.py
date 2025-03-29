import requests
import re
import logging

# Figma API Token (Replace with your actual token)
FIGMA_API_TOKEN = "figd_6wWgkoTn-oST522A4G6IyOcweCqPCeKyS8a6CQoj"

def extract_file_key(figma_url):
    """
    Extracts the file key from a given Figma URL.
    Supports both `/file/` and `/design/` URL formats.
    """
    match = re.search(r"https://www\.figma\.com/(?:file|design)/([a-zA-Z0-9-_]+)", figma_url)
    if match:
        return match.group(1)
    return None

def extract_frame_details(node):
    """
    Recursively extracts frame details along with all child elements.
    """
    if not isinstance(node, dict):
        return {}

    node_data = {
        "id": node.get("id"),
        "name": node.get("name", "Unnamed"),
        "type": node.get("type", "UNKNOWN"),
        "visible": node.get("visible", True),
        "position": node.get("absoluteBoundingBox", {}).get("x", None),
        "size": {
            "width": node.get("absoluteBoundingBox", {}).get("width"),
            "height": node.get("absoluteBoundingBox", {}).get("height"),
        },
        "background_color": node.get("backgroundColor", {}),
        "children": []
    }

    # Recursively process children
    if "children" in node:
        for child in node["children"]:
            node_data["children"].append(extract_frame_details(child))

    return node_data

def extract_important_frame_data(figma_json):
    """
    Extracts all frame-wise key details along with their child components recursively.
    """
    important_data = {}

    try:
        document = figma_json.get("document", {})
        if not document:
            return {"error": "Invalid JSON structure. 'document' key missing."}

        # Process all pages
        for page in document.get("children", []):
            page_name = page.get("name", "Unknown Page")
            page_data = []

            for frame in page.get("children", []):
                frame_details = extract_frame_details(frame)
                page_data.append(frame_details)

            important_data[page_name] = page_data

        return important_data

    except Exception as e:
        logging.error(f"Error extracting frame data: {str(e)}")
        return {"error": "Failed to process frame data"}

def fetch_figma_json(figma_url):
    """
    Fetches and processes the Figma JSON from the given URL.
    Extracts all frame details with hierarchical child structures.
    """
    try:
        file_key = extract_file_key(figma_url)
        if not file_key:
            return {"error": "Invalid Figma URL"}

        # API Endpoint
        url = f"https://api.figma.com/v1/files/{file_key}"

        # Headers with API Token
        headers = {
            "X-Figma-Token": FIGMA_API_TOKEN
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logging.error(f"HTTP Error {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code} - {response.text}"}

        # Check if response is empty
        if not response.text.strip():
            logging.error("Empty response received from Figma API.")
            return {"error": "Empty response from Figma API"}

        # Try to parse JSON
        try:
            figma_json = response.json()
        except requests.exceptions.JSONDecodeError:
            logging.error("Invalid JSON received from Figma API.")
            return {"error": "Invalid JSON received from API"}

        extracted_data = extract_important_frame_data(figma_json)
        return extracted_data

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
        return {"error": f"Request failed: {str(e)}"}
