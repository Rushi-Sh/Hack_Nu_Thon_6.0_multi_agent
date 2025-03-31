import os
import json
import argparse
import logging
from dotenv import load_dotenv

# Import scraping functions from the first module
from paste import (
    setup_driver, get_relative_path, ensure_directory, save_file,
    download_file, scrape_website
)

# Import PDF extraction and summarization functions
def import_pdf_functions():
    global extract_text, split_text, summarize_text
    
    # These functions are from your PDF processing module
    import fitz  # PyMuPDF
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain_groq import ChatGroq
    import tiktoken
    
    # Load API key
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=os.getenv("GROQ_API_KEY"))
    
    # Count tokens
    def count_tokens(text):
        return len(tiktoken.encoding_for_model("gpt-4").encode(text))
    
    # Extract text from PDF
    def extract_text(pdf_bytes):
        return "\n".join(page.get_text("text").strip() for page in fitz.open(stream=pdf_bytes, filetype="pdf"))
    
    # Split text into chunks
    def split_text(text, max_tokens=2000):
        words, chunks, chunk = text.split(), [], []
        tokens = 0
        for word in words:
            word_tokens = count_tokens(word)
            if tokens + word_tokens > max_tokens:
                chunks.append(" ".join(chunk))
                chunk, tokens = [word], word_tokens
            else:
                chunk.append(word)
                tokens += word_tokens
        if chunk:
            chunks.append(" ".join(chunk))
        return chunks
    
    # Summarize document
    def summarize_text(pdf_text):
        if not pdf_text.strip():
            return "No text found."
        
        prompt = PromptTemplate(
            input_variables=["chunk"],
            template="""
            You are an expert software QA analyst. Based on the following section of a requirements document, 
            create a concise and structured summary that outlines key testable components.
            
            Document section:
            {chunk}
            
            Format your response as a structured list of requirements that can be translated into test cases.
            """
        )
        
        summaries = [(prompt | groq_llm).invoke({"chunk": chunk}).content.strip() for chunk in split_text(pdf_text)]
        return "\n".join(summaries)
    
    return extract_text, split_text, summarize_text

# Import Figma API functions
def import_figma_functions():
    global extract_file_key, categorize_uiux_elements, extract_uiux_details, extract_uiux_data, fetch_figma_uiux_json
    
    import re
    import requests
    import json
    import time
    
    # Extract file key from Figma URL
    def extract_file_key(figma_url):
        match = re.search(r"https://www\.figma\.com/(?:file|design)/([a-zA-Z0-9-_]+)", figma_url)
        return match.group(1) if match else None
    
    # Categorize UI/UX elements
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
        headers = {"X-Figma-Token": os.getenv("FIGMA_API_TOKEN")}
        
        for attempt in range(5):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 429:
                    time.sleep(2 ** attempt)
                    continue
                response.raise_for_status()
                return extract_uiux_data(json.loads(response.content))
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching Figma JSON: {e}")
                time.sleep(2 ** attempt)
        
        return {"error": "Failed to fetch data from Figma API."}
    
    return extract_file_key, categorize_uiux_elements, extract_uiux_details, extract_uiux_data, fetch_figma_uiux_json

# Import functions from the Flask app
def import_flask_functions():
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    import subprocess
    
    def create_flask_app():
        app = Flask(__name__)
        CORS(app, resources={r"/*": {"origins": "*"}})
        
        # Directory to save uploaded test files
        UPLOAD_FOLDER = 'uploads'
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        @app.route('/upload', methods=['POST'])
        def upload_file():
            if 'file' not in request.files:
                print("No 'file' found in request.files")
                return jsonify({'error': 'No file part', 'available_keys': list(request.files.keys())}), 400
        
            file = request.files['file']
            if file.filename == '':
                print("Filename is empty")
                return jsonify({'error': 'No selected file'}), 400
        
            print(f"Received file: {file.filename}")
            
            # Save the uploaded file
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            print(f"File saved to {file_path}")
        
            # Run the Selenium test
            try:
                print(f"Running command: node {file_path}")
                result = subprocess.run(['node', file_path], capture_output=True, text=True)
                output = result.stdout
                error = result.stderr
                print(f"Command return code: {result.returncode}")
                print(f"Command output: {output}")
                print(f"Command error: {error}")
        
                if result.returncode == 0:
                    return jsonify({'message': 'Test executed successfully', 'output': output, 'file_path': file_path}), 200
                else:
                    return jsonify({'error': 'Test execution failed', 'details': error}), 500
            except Exception as e:
                print(f"Exception occurred: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        # Simple test endpoint
        @app.route('/test', methods=['GET'])
        def test_cors():
            return jsonify({'message': 'CORS is enabled'}), 200
        
        return app
    
    return create_flask_app

# Main Test Generator Agent class
class SeleniumTestGenerator:
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Load environment variables
        load_dotenv()
        
        # Import PDF functions
        self.extract_text, self.split_text, self.summarize_text = import_pdf_functions()
        
        # Import Figma functions
        self.extract_file_key, self.categorize_uiux_elements, self.extract_uiux_details, \
        self.extract_uiux_data, self.fetch_figma_uiux_json = import_figma_functions()
        
        # Import Flask app creator
        self.create_flask_app = import_flask_functions()
        
        # Set up paths
        self.OUTPUT_DIR = "test_output"
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
    
    def scrape_and_analyze_website(self, url):
        """Scrape website and analyze its structure"""
        self.logger.info(f"Starting website scraping for: {url}")
        output_folder = os.path.join(self.OUTPUT_DIR, "scraped_site")
        scrape_website(url, output_folder)
        
        # Analyze site structure from scraped content
        index_path = os.path.join(output_folder, "index.html")
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract page structure info
            soup = BeautifulSoup(html_content, 'html.parser')
            page_structure = {
                'title': soup.title.string if soup.title else "No title",
                'forms': len(soup.find_all('form')),
                'links': len(soup.find_all('a')),
                'buttons': len(soup.find_all('button')),
                'inputs': len(soup.find_all('input')),
                'images': len(soup.find_all('img')),
                'headings': {
                    'h1': len(soup.find_all('h1')),
                    'h2': len(soup.find_all('h2')), 
                    'h3': len(soup.find_all('h3'))
                }
            }
            
            # Identify interactive elements
            interactive_elements = []
            for element in soup.find_all(['button', 'a', 'input', 'select', 'textarea']):
                elem_id = element.get('id', '')
                elem_class = ' '.join(element.get('class', []))
                elem_text = element.text.strip()
                elem_type = element.name
                
                if elem_type == 'input':
                    elem_input_type = element.get('type', 'text')
                    elem_type = f"input[type='{elem_input_type}']"
                
                selector = self._build_selector(element)
                if selector:
                    interactive_elements.append({
                        'element_type': elem_type,
                        'id': elem_id,
                        'class': elem_class,
                        'text': elem_text,
                        'selector': selector
                    })
            
            # Save analysis
            site_analysis = {
                'page_structure': page_structure,
                'interactive_elements': interactive_elements,
                'scraped_location': output_folder
            }
            
            with open(os.path.join(self.OUTPUT_DIR, 'site_analysis.json'), 'w', encoding='utf-8') as f:
                json.dump(site_analysis, f, indent=2)
            
            self.logger.info(f"Website analysis completed: {len(interactive_elements)} interactive elements found")
            return site_analysis
        else:
            self.logger.error(f"Failed to find index.html in scraped content")
            return None
    
    def _build_selector(self, element):
        """Build a CSS selector for the element"""
        if element.get('id'):
            return f"#{element['id']}"
        
        if element.get('class'):
            class_selector = '.{}'.format('.'.join(element['class']))
            return class_selector
        
        # Fallback to element type with nth-child
        parent = element.parent
        if parent:
            siblings = parent.find_all(element.name, recursive=False)
            if len(siblings) > 1:
                for i, sibling in enumerate(siblings):
                    if sibling == element:
                        return f"{element.name}:nth-child({i+1})"
        
        return element.name
    
    def extract_requirements_from_pdf(self, pdf_path):
        """Extract testing requirements from SRS PDF"""
        self.logger.info(f"Extracting requirements from: {pdf_path}")
        
        with open(pdf_path, "rb") as f:
            pdf_text = self.extract_text(f.read())
            
        # Generate summarized requirements
        requirements = self.summarize_text(pdf_text)
        
        with open(os.path.join(self.OUTPUT_DIR, 'requirements.txt'), 'w', encoding='utf-8') as f:
            f.write(requirements)
        
        self.logger.info(f"Requirements extraction completed")
        return requirements
    
    def get_figma_data(self, figma_url):
        """Get UI/UX data from Figma"""
        self.logger.info(f"Fetching Figma data from: {figma_url}")
        figma_data = self.fetch_figma_uiux_json(figma_url)
        
        if "error" in figma_data:
            self.logger.error(f"Error in Figma data: {figma_data['error']}")
            return None
        
        # Save to file
        with open(os.path.join(self.OUTPUT_DIR, 'figma_data.json'), 'w', encoding='utf-8') as f:
            json.dump(figma_data, f, indent=2)
        
        self.logger.info(f"Figma data extraction completed")
        return figma_data
    
    def generate_test_cases(self, site_analysis, requirements, figma_data):
        """Generate test cases based on collected data"""
        self.logger.info("Generating test cases")
        
        # Prepare prompt for LLM
        prompt = PromptTemplate(
            input_variables=["site_analysis", "requirements", "figma_data"],
            template="""
            Generate a comprehensive set of Selenium test cases for a web application based on the following inputs:
            
            WEBSITE STRUCTURE: {site_analysis}
            
            REQUIREMENTS: {requirements}
            
            FIGMA UI DATA: {figma_data}
            
            Create test cases that verify:
            1. Core functionality based on requirements
            2. UI/UX elements match Figma designs
            3. Form submission and validation
            4. Navigation flows
            5. Error handling
            
            For each test case, provide:
            1. Title
            2. Description
            3. Preconditions
            4. Test steps
            5. Expected results
            
            Format your response as a JSON array of test cases.
            """
        )
        
        # Convert input data to string format for LLM
        site_analysis_str = json.dumps(site_analysis)
        figma_data_str = json.dumps(figma_data)
        
        # Generate test cases
        response = (prompt | groq_llm).invoke({
            "site_analysis": site_analysis_str,
            "requirements": requirements,
            "figma_data": figma_data_str
        })
        
        # Extract and parse JSON
        try:
            test_cases = json.loads(response.content)
            with open(os.path.join(self.OUTPUT_DIR, 'test_cases.json'), 'w', encoding='utf-8') as f:
                json.dump(test_cases, f, indent=2)
            
            self.logger.info(f"Generated {len(test_cases)} test cases")
            return test_cases
        except json.JSONDecodeError:
            self.logger.error("Failed to parse generated test cases as JSON")
            # Save raw response
            with open(os.path.join(self.OUTPUT_DIR, 'test_cases_raw.txt'), 'w', encoding='utf-8') as f:
                f.write(response.content)
            return None
    
    def generate_selenium_code(self, test_cases):
        """Generate Selenium code from test cases"""
        self.logger.info("Generating Selenium code")
        
        # Prepare prompt for code generation
        prompt = PromptTemplate(
            input_variables=["test_cases"],
            template="""
            Generate Selenium WebDriver JavaScript code for the following test cases:
            
            {test_cases}
            
            For each test case, create JavaScript functions using modern Selenium syntax with:
            - Proper error handling
            - Clear comments
            - CSS selectors for element identification
            - Assertions for expected results
            - Proper setup and teardown
            
            Use Node.js with Selenium WebDriver. Include all necessary package imports and setup.
            Return only the complete, ready-to-run test code.
            """
        )
        
        # Generate code
        response = (prompt | groq_llm).invoke({
            "test_cases": json.dumps(test_cases)
        })
        
        # Extract code
        selenium_code = response.content
        
        # Save generated code
        selenium_file = os.path.join(self.OUTPUT_DIR, 'selenium_tests.js')
        with open(selenium_file, 'w', encoding='utf-8') as f:
            f.write(selenium_code)
        
        self.logger.info(f"Selenium code generated: {selenium_file}")
        return selenium_file
    
    def run_tests(self, selenium_file):
        """Run the generated Selenium tests"""
        self.logger.info(f"Running Selenium tests: {selenium_file}")
        
        try:
            result = subprocess.run(['node', selenium_file], capture_output=True, text=True)
            output = result.stdout
            error = result.stderr
            
            with open(os.path.join(self.OUTPUT_DIR, 'test_results.txt'), 'w', encoding='utf-8') as f:
                f.write(f"Output:\n{output}\n\nErrors:\n{error}")
            
            return {
                'success': result.returncode == 0,
                'output': output,
                'error': error
            }
        except Exception as e:
            self.logger.error(f"Error running tests: {str(e)}")
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
    
    def start_server(self, port=5000):
        """Start Flask server for test execution"""
        app = self.create_flask_app()
        self.logger.info(f"Starting server on port {port}")
        app.run(debug=True, port=port)
    
    def run_complete_pipeline(self, website_url, pdf_path, figma_url, run_tests=True):
        """Run the complete test generation pipeline"""
        self.logger.info("Starting complete test generation pipeline")
        
        # Step 1: Scrape and analyze website
        site_analysis = self.scrape_and_analyze_website(website_url)
        if not site_analysis:
            return {"error": "Failed to analyze website"}
        
        # Step 2: Extract requirements from PDF
        requirements = self.extract_requirements_from_pdf(pdf_path)
        if not requirements:
            return {"error": "Failed to extract requirements"}
        
        # Step 3: Get Figma data
        figma_data = self.get_figma_data(figma_url)
        if not figma_data:
            return {"error": "Failed to get Figma data"}
        
        # Step 4: Generate test cases
        test_cases = self.generate_test_cases(site_analysis, requirements, figma_data)
        if not test_cases:
            return {"error": "Failed to generate test cases"}
        
        # Step 5: Generate Selenium code
        selenium_file = self.generate_selenium_code(test_cases)
        
        # Step 6: Run tests if requested
        test_results = None
        if run_tests:
            test_results = self.run_tests(selenium_file)
        
        return {
            "status": "success",
            "site_analysis": os.path.join(self.OUTPUT_DIR, 'site_analysis.json'),
            "requirements": os.path.join(self.OUTPUT_DIR, 'requirements.txt'),
            "figma_data": os.path.join(self.OUTPUT_DIR, 'figma_data.json'),
            "test_cases": os.path.join(self.OUTPUT_DIR, 'test_cases.json'),
            "selenium_code": selenium_file,
            "test_results": test_results
        }

# Command-line interface
def main():
    parser = argparse.ArgumentParser(description='Selenium Test Generator')
    parser.add_argument('--website', required=True, help='URL of the website to scrape')
    parser.add_argument('--pdf', required=True, help='Path to the SRS PDF file')
    parser.add_argument('--figma', required=True, help='Figma URL')
    parser.add_argument('--no-run', action='store_true', help='Skip running tests')
    parser.add_argument('--server', action='store_true', help='Start Flask server')
    parser.add_argument('--port', type=int, default=5000, help='Port for Flask server')
    
    args = parser.parse_args()
    
    generator = SeleniumTestGenerator()
    
    if args.server:
        generator.start_server(args.port)
    else:
        result = generator.run_complete_pipeline(
            args.website,
            args.pdf,
            args.figma,
            not args.no_run
        )
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()