import requests
import re
import logging
import orjson
import tiktoken

FIGMA_API_TOKEN = "figd_6wWgkoTn-oST522A4G6IyOcweCqPCeKyS8a6CQoj"
TOKEN_LIMIT = 6000  # Adjust to stay within API constraints

# Extract file key from Figma URL
def extract_file_key(figma_url):
    match = re.search(r"https://www\.figma\.com/(?:file|design)/([a-zA-Z0-9-_]+)", figma_url)
    return match.group(1) if match else None

# Process a Figma frame node efficiently
def extract_frame_details(node):
    if not isinstance(node, dict):
        return {}
    
    return {
        "id": node.get("id"),
        "name": node.get("name", "Unnamed"),
        "type": node.get("type", "UNKNOWN"),
        "size": {  # Only store essential bounding details
            "w": node.get("absoluteBoundingBox", {}).get("width"),
            "h": node.get("absoluteBoundingBox", {}).get("height"),
        },
        "children": [extract_frame_details(child) for child in node.get("children", [])],
    }

# Extract relevant data from Figma JSON
def extract_important_frame_data(figma_json):
    document = figma_json.get("document", {})
    if not document:
        return {"error": "Invalid JSON structure. 'document' key missing."}
    
    return {
        page.get("name", "Unknown Page"): [extract_frame_details(frame) for frame in page.get("children", [])]
        for page in document.get("children", [])
    }

# Token-aware JSON chunking
def chunk_json(json_data, max_tokens=TOKEN_LIMIT):
    encoding = tiktoken.encoding_for_model("gpt-4")
    json_str = orjson.dumps(json_data).decode()  # Use orjson for compact serialization
    
    words = json_str.split()
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for word in words:
        token_count = len(encoding.encode(word))
        if current_tokens + token_count > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_tokens = 0
        
        current_chunk.append(word)
        current_tokens += token_count
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

# Fetch and process Figma JSON
def fetch_figma_json(figma_url):
    file_key = extract_file_key(figma_url)
    if not file_key:
        return {"error": "Invalid Figma URL"}

    url = f"https://api.figma.com/v1/files/{file_key}"
    headers = {"X-Figma-Token": FIGMA_API_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.error(f"HTTP Error {response.status_code}: {response.text}")
        return {"error": f"HTTP {response.status_code} - {response.text}"}

    figma_json = response.json()
    extracted_data = extract_important_frame_data(figma_json)
    
    # Handle large JSON responses by splitting into chunks
    chunked_data = chunk_json(extracted_data)
    
    return {"chunks": chunked_data}

if __name__ == "__main__":
    figma_url = "https://www.figma.com/design/IDuTOIkVefgkJ6lOvFvGpr/Untitled?node-id=0-1&t=BXHmxq1xN3YM0kuh-1"
    figma_data = fetch_figma_json(figma_url)
    
    if "error" in figma_data:
        print("Error:", figma_data["error"])
    else:
        print("Extracted Data Chunks:")
        for i, chunk in enumerate(figma_data["chunks"]):
            print(f"\n🔹 Chunk {i+1}:\n{chunk[:500]}")
