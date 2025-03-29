import requests
import json

# Figma API Token (Keep it secure)
FIGMA_API_TOKEN = "figd_6wWgkoTn-oST522A4G6IyOcweCqPCeKyS8a6CQoj"

# File Key from Figma URL
FILE_KEY = "qyiTc7JlJVT2v3uW5Rwq8x"

# Figma API Endpoint
FIGMA_API_URL = f"https://api.figma.com/v1/files/{FILE_KEY}"

# API Request Headers
headers = {"X-Figma-Token": FIGMA_API_TOKEN}

# Fetch Data from Figma API
response = requests.get(FIGMA_API_URL, headers=headers)

if response.status_code == 200:
    figma_data = response.json()
    
    # Save JSON data to a file
    with open("figma_data.json", "w", encoding="utf-8") as json_file:
        json.dump(figma_data, json_file, indent=4, ensure_ascii=False)
    
    print("✅ Figma data saved successfully as 'figma_data.json'\n")

    # Extracting Headers
    print("🔹 Response Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")

    # Extracting Top-Level Keys
    print("\n🔹 Top-Level JSON Keys:")
    for key, value in figma_data.items():
        print(f"  {key} ➝ {type(value).__name__}")

    # Extracting Some Nested Keys
    if "document" in figma_data and "children" in figma_data["document"]:
        print("\n🔹 Sample Nested Keys in 'document':")
        for child in figma_data["document"]["children"]:
            print(f"  - {child.get('id', 'No ID')} ➝ {child.get('name', 'No Name')} ({child.get('type', 'No Type')})")

else:
    print(f"❌ Error: {response.status_code}, {response.text}")
