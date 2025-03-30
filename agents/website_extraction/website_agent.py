import os
from playwright.sync_api import sync_playwright
import tiktoken
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Function to chunk text efficiently for LLM token limits
def chunk_text(text, max_tokens=2000):
    encoding = tiktoken.encoding_for_model("gpt-4")
    words = text.split()
    chunks, current_chunk, current_tokens = [], [], 0
    
    for word in words:
        token_count = len(encoding.encode(word))
        if current_tokens + token_count > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk, current_tokens = [], 0
        current_chunk.append(word)
        current_tokens += token_count
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

# Extract structured elements for Selenium JS script generation
def extract_elements_for_selenium(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(url, timeout=15000, wait_until="networkidle")

            # Extract Metadata
            title = page.title()
            meta_tags = {meta.get_attribute("name"): meta.get_attribute("content") for meta in page.locator("meta").all() if meta.get_attribute("name")}

            # Extract Interactive Elements
            buttons = [{
                "text": btn.inner_text(),
                "selector": btn.evaluate("el => el.outerHTML")
            } for btn in page.locator("button").all()]
            
            inputs = [{
                "name": inp.get_attribute("name"),
                "type": inp.get_attribute("type"),
                "id": inp.get_attribute("id"),
                "selector": inp.evaluate("el => el.outerHTML")
            } for inp in page.locator("input").all() if inp.get_attribute("name")]
            
            links = [{
                "href": a.get_attribute("href"),
                "text": a.inner_text()
            } for a in page.locator("a").all() if a.get_attribute("href")]
            
            forms = [{
                "action": form.get_attribute("action"),
                "method": form.get_attribute("method"),
                "selector": form.evaluate("el => el.outerHTML")
            } for form in page.locator("form").all()]

            # Extract JavaScript Execution & API Calls
            scripts = [script.inner_text() for script in page.locator("script").all()]
            json_ld_data = [script.inner_text() for script in page.locator("script[type='application/ld+json']").all()]

            # Extract UI-related attributes (for visual validation)
            css_classes = [el.get_attribute("class") for el in page.locator("*[class]").all()]
            
            # Extract Elements for Selenium Test Cases
            selenium_elements = []
            for btn in buttons:
                selenium_elements.append({
                    "action": "click",
                    "type": "button",
                    "selector": btn["selector"],
                    "text": btn["text"]
                })
            for inp in inputs:
                selenium_elements.append({
                    "action": "input",
                    "type": inp["type"],
                    "selector": inp["selector"],
                    "name": inp["name"]
                })
            for link in links:
                selenium_elements.append({
                    "action": "navigate",
                    "type": "link",
                    "href": link["href"],
                    "text": link["text"]
                })
            
            browser.close()
            
            extracted_data = {
                "metadata": {"title": title, "meta_tags": meta_tags},
                "selenium_test_elements": selenium_elements,
                "frontend_testing": {
                    "buttons": buttons,
                    "input_fields": inputs,
                    "forms": forms,
                    "links": links,
                    "scripts": chunk_text("\n".join(scripts)),
                    "json_ld": json_ld_data
                },
                "visual_testing": {
                    "css_classes": css_classes
                }
            }
            
            return extracted_data
        
        except Exception as e:
            browser.close()
            return {"error": f"Failed to extract content: {str(e)}"}

# ✅ Run the extraction pipeline
if __name__ == "__main__":
    url = "https://urbansnap.vercel.app/"  # Replace with the target URL
    extracted_data = extract_elements_for_selenium(url)
    
    if "error" not in extracted_data:
        with open("selenium_testing_data.json", "w") as file:
            json.dump(extracted_data, file, indent=2)
        print("\n🔹 Extracted Data Saved to selenium_testing_data.json")
    else:
        print("\n❌ Error:", extracted_data["error"])