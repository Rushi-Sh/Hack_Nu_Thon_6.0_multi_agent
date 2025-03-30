import os
from playwright.sync_api import sync_playwright
import tiktoken
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Function to chunk text efficiently for LLM token limits
def chunk_text(text, max_tokens=6000):
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

# Extract important elements for frontend & UI/UX testing
def extract_important_elements(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(url, timeout=15000, wait_until="networkidle")

            # Extract Metadata
            title = page.title()
            meta_tags = {meta.get_attribute("name"): meta.get_attribute("content") for meta in page.locator("meta").all() if meta.get_attribute("name")}
            
            # Extract Interactive Elements (for frontend testing)
            buttons = [btn.inner_text() for btn in page.locator("button").all()]
            inputs = [inp.get_attribute("name") for inp in page.locator("input").all() if inp.get_attribute("name")]
            forms = [form.get_attribute("action") for form in page.locator("form").all() if form.get_attribute("action")]
            links = [a.get_attribute("href") for a in page.locator("a").all() if a.get_attribute("href")]

            # Extract JavaScript Execution and API Calls (for integration & performance testing)
            scripts = [script.inner_text() for script in page.locator("script").all()]
            json_ld_data = [script.inner_text() for script in page.locator("script[type='application/ld+json']").all()]

            # Extract UI-related attributes (for visual testing)
            css_classes = [el.get_attribute("class") for el in page.locator("*[class]").all()]
            
            # ✅ Extract Lazy-loaded & AJAX Content
            dynamic_elements = page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('*'))
                        .filter(el => el.hasAttributes())
                        .map(el => {
                            let attributes = {};
                            for (let attr of el.attributes) {
                                if (attr.name.startsWith('data-')) {
                                    attributes[attr.name] = attr.value;
                                }
                            }
                            return attributes;
                        }).filter(attr => Object.keys(attr).length > 0);
                }
            """)

            browser.close()

            extracted_data = {
                "metadata": {"title": title, "meta_tags": meta_tags},
                "frontend_testing": {
                    "buttons": buttons,
                    "input_fields": inputs,
                    "forms": forms,
                    "links": links,
                    "scripts": chunk_text("\n".join(scripts)),
                    "json_ld": json_ld_data
                },
                "visual_testing": {
                    "css_classes": css_classes,
                    "dynamic_content": chunk_text(str(dynamic_elements))
                }
            }
            
            return extracted_data
        
        except Exception as e:
            browser.close()
            return {"error": f"Failed to extract content: {str(e)}"}

# ✅ Run the pipeline
if __name__ == "__main__":
    url = "https://google.com"  # Replace with the target URL
    extracted_data = extract_important_elements(url)
    
    if "error" not in extracted_data:
        with open("testing_data.json", "w") as file:
            json.dump(extracted_data, file, indent=2)
        print("\n🔹 Extracted Data Saved to testing_data.json")
    else:
        print("\n❌ Error:", extracted_data["error"])