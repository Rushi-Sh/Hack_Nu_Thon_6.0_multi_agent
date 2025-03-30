import requests
import re
import logging
import orjson
import tiktoken

# API Token and Limits
FIGMA_API_TOKEN = "figd_6wWgkoTn-oST522A4G6IyOcweCqPCeKyS8a6CQoj"
TOKEN_LIMIT = 3000  # Adjust for API constraints

# Extract file key from Figma URL
def extract_file_key(figma_url):
    match = re.search(r"https://www\.figma\.com/(?:file|design)/([a-zA-Z0-9-_]+)", figma_url)
    return match.group(1) if match else None

# Categorize UI/UX elements for structured testing
def categorize_uiux_elements(node):
    element_type = node.get("type", "UNKNOWN").lower()
    category = "Uncategorized"

    if element_type in ["frame", "container"]:
        category = "Layout_agent"
    elif "responsive" in node.get("name", "").lower():
        category = "Responsiveness_agent"
    elif "contrast" in node.get("name", "").lower():
        category = "Accessibility_agent"
    elif "tooltip" in node.get("name", "").lower():
        category = "Usability_agent"

    return category

# Extract only relevant UI/UX details, ensuring API limits are respected
def extract_uiux_details(node):
    if not isinstance(node, dict):
        return {}

    element_category = categorize_uiux_elements(node)
    return {
        "id": node.get("id"),
        "name": node.get("name", "Unnamed"),
        "type": node.get("type", "UNKNOWN"),
        "category": element_category,
        "size": {
            "w": node.get("absoluteBoundingBox", {}).get("width"),
            "h": node.get("absoluteBoundingBox", {}).get("height"),
        },
        "children": [extract_uiux_details(child) for child in node.get("children", [])],
    }

# Trim JSON to fit within API token limits
def trim_json(json_data, max_tokens=TOKEN_LIMIT):
    json_str = orjson.dumps(json_data).decode("utf-8")
    if len(json_str) > max_tokens:
        json_str = json_str[:max_tokens]  # Truncate the JSON to fit the limit
    return orjson.loads(json_str)  # Convert back to dictionary

# Extract UI/UX structured data from Figma JSON
def extract_uiux_data(figma_json):
    document = figma_json.get("document", {})
    if not document:
        return {"error": "Invalid JSON structure. 'document' key missing."}

    extracted_data = {"UI_UX_Testing": []}

    for page in document.get("children", []):
        for frame in page.get("children", []):
            frame_details = extract_uiux_details(frame)
            extracted_data["UI_UX_Testing"].append(frame_details)

    return trim_json(extracted_data)  # Trim JSON if needed

# Fetch and process Figma JSON while handling large responses
def fetch_figma_uiux_json(figma_url):
    file_key = extract_file_key(figma_url)
    if not file_key:
        return {"error": "Invalid Figma URL"}

    url = f"https://api.figma.com/v1/files/{file_key}"
    headers = {"X-Figma-Token": FIGMA_API_TOKEN}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP Request Failed: {e}")
        return {"error": f"HTTP Request Failed: {str(e)}"}

    figma_json = response.json()
    extracted_data = extract_uiux_data(figma_json)

    # Save optimized extracted data to a JSON file
    with open("figma_uiux_data.json", "wb") as f:
        f.write(orjson.dumps(extracted_data, option=orjson.OPT_INDENT_2))

    return extracted_data

if __name__ == "__main__":
    figma_url = "https://www.figma.com/design/jEwcn0Rt7XinS4hTiKgGAB/HackNUthonTest?node-id=0-1&p=f&t=iMKT9tbeDYBjza3Z-0"
    figma_data = fetch_figma_uiux_json(figma_url)
    
    if "error" in figma_data:
        print("Error:", figma_data["error"])
    else:
        print("UI/UX Testing Data Extracted and Saved to 'figma_uiux_data.json'")
