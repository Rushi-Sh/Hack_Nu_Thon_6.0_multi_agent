import requests
import re
import logging
import orjson
import time

FIGMA_API_TOKEN = "figd_6wWgkoTn-oST522A4G6IyOcweCqPCeKyS8a6CQoj"

# Extract file key from Figma URL
def extract_file_key(figma_url):
    match = re.search(r"https://www\.figma\.com/(?:file|design)/([a-zA-Z0-9-_]+)", figma_url)
    return match.group(1) if match else None

# Categorize UI/UX elements (optimized to exclude non-essential elements)
def categorize_uiux_elements(node):
    name = node.get("name", "").lower()
    
    # Keep only core interactive components
    usability_keywords = ["button", "form", "input", "tooltip", "modal", "dropdown", "checkbox", "radio", "link", "interaction"]
    layout_keywords = ["frame", "section", "component"]

    if any(keyword in name for keyword in usability_keywords):
        return "Usability_agent"
    if node.get("type", "").lower() in layout_keywords:
        return "Layout_agent"
    
    return None  # Ignore decorative elements like vector, line, etc.


# Extract UI/UX details
def extract_uiux_details(node):
    category = categorize_uiux_elements(node)
    if not category:
        return None
    return {
        "id": node.get("id"),
        "name": node.get("name", "Unnamed"),
        "type": node.get("type", "UNKNOWN"),
        "category": category,
        "size": node.get("absoluteBoundingBox", {})
    }

# Recursively extract UI/UX data
def extract_uiux_data(figma_json):
    extracted_data = {"Layout_agent": [], "Usability_agent": []}
    
    def process_nodes(nodes):
        for node in nodes:
            details = extract_uiux_details(node)
            if details:
                extracted_data[details["category"]].append(details)
            if "children" in node:
                process_nodes(node["children"])
    
    process_nodes(figma_json.get("document", {}).get("children", []))
    return extracted_data

# Fetch Figma JSON
def fetch_figma_uiux_json(figma_url):
    file_key = extract_file_key(figma_url)
    if not file_key:
        return {"error": "Invalid Figma URL"}
    
    url = f"https://api.figma.com/v1/files/{file_key}"
    headers = {"X-Figma-Token": FIGMA_API_TOKEN}
    
    for attempt in range(5):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            response.raise_for_status()
            return extract_uiux_data(orjson.loads(response.content))
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching Figma JSON: {e}")
            time.sleep(2 ** attempt)
    
    return {"error": "Failed to fetch data from Figma API."}

if __name__ == "__main__":
    figma_url = "https://www.figma.com/design/jEwcn0Rt7XinS4hTiKgGAB/HackNUthonTest?node-id=0-1&p=f&t=iMKT9tbeDYBjza3Z-0"
    figma_data = fetch_figma_uiux_json(figma_url)
    
    if "error" in figma_data:
        print("\n❌ Error:", figma_data["error"])
    else:
        with open("figma_uiux_data.json", "wb") as f:
            f.write(orjson.dumps(figma_data, option=orjson.OPT_INDENT_2))
        print("\n✅ UI/UX Testing Data Extracted and Saved")