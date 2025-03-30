import requests
import re
import logging
import orjson
import time

FIGMA_API_TOKEN = "figd_6wWgkoTn-oST522A4G6IyOcweCqPCeKyS8a6CQoj"
MAX_RETRIES = 5  # Retry attempts for API requests

# Extract file key from Figma URL
def extract_file_key(figma_url):
    match = re.search(r"https://www\.figma\.com/(?:file|design)/([a-zA-Z0-9-_]+)", figma_url)
    return match.group(1) if match else None

# Categorize UI/UX elements for testing agents
def categorize_uiux_elements(node):
    element_type = node.get("type", "UNKNOWN").lower()
    name = node.get("name", "").lower()

    layout_keywords = ["frame", "group", "container", "section", "component"]
    usability_keywords = ["button", "form", "input", "tooltip", "modal", "dropdown", "checkbox", "radio", "link", "interaction"]

    if element_type in layout_keywords:
        return "Layout_agent"
    if any(keyword in name for keyword in usability_keywords):
        return "Usability_agent"
    
    return None  # Ignore non-relevant elements

# Extract relevant UI/UX details from a Figma node
def extract_uiux_details(node):
    if not isinstance(node, dict):
        return None

    category = categorize_uiux_elements(node)
    if not category:
        return None  # Skip irrelevant elements

    return {
        "id": node.get("id"),
        "name": node.get("name", "Unnamed"),
        "type": node.get("type", "UNKNOWN"),
        "category": category,
        "size": {
            "width": node.get("absoluteBoundingBox", {}).get("width"),
            "height": node.get("absoluteBoundingBox", {}).get("height"),
        }
    }

# Recursively extract and structure UI/UX elements from the Figma JSON
def extract_uiux_data(figma_json):
    document = figma_json.get("document", {})
    if not document:
        return {"error": "Invalid JSON structure. 'document' key missing."}

    extracted_data = {
        "Layout_agent": [],
        "Usability_agent": []
    }

    def process_nodes(nodes):
        for node in nodes:
            node_details = extract_uiux_details(node)
            if node_details:
                category = node_details["category"]
                extracted_data[category].append(node_details)
            
            # Recursively process children
            if "children" in node:
                process_nodes(node["children"])
    
    process_nodes(document.get("children", []))
    return extracted_data

# Fetch and process Figma JSON with retries
def fetch_figma_uiux_json(figma_url):
    file_key = extract_file_key(figma_url)
    if not file_key:
        return {"error": "Invalid Figma URL"}

    url = f"https://api.figma.com/v1/files/{file_key}"
    headers = {"X-Figma-Token": FIGMA_API_TOKEN}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 429:  # Handle rate limiting
                wait_time = 2 ** attempt  # Exponential backoff
                logging.warning(f"Rate limited. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()  # Raise error for HTTP failures

            try:
                figma_json = orjson.loads(response.content)  # Use orjson for efficiency
            except orjson.JSONDecodeError as e:
                logging.error(f"JSON Decode Error: {e}")
                return {"error": "Invalid JSON received from Figma API"}

            extracted_data = extract_uiux_data(figma_json)

            # Save extracted data to a JSON file
            with open("figma_uiux_data.json", "wb") as f:
                f.write(orjson.dumps(extracted_data, option=orjson.OPT_INDENT_2))

            return extracted_data

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching Figma JSON (Attempt {attempt}/{MAX_RETRIES}): {e}")
            time.sleep(2 ** attempt)  # Retry with exponential backoff

    return {"error": "Failed to fetch data from Figma API after multiple attempts."}

if __name__ == "__main__":
    figma_url = "https://www.figma.com/design/jEwcn0Rt7XinS4hTiKgGAB/HackNUthonTest?node-id=0-1&p=f&t=iMKT9tbeDYBjza3Z-0"
    figma_data = fetch_figma_uiux_json(figma_url)

    if "error" in figma_data:
        print("\n❌ Error:", figma_data["error"])
    else:
        print("\n✅ UI/UX Testing Data Extracted and Saved to 'figma_uiux_data.json'")
