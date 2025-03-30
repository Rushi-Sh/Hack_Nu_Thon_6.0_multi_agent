import langgraph
import json
import sys
import os
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test case generators
from test_case_generation.visual_testing.ui_ux_parent import uiux_pipeline
from test_case_generation.frontend_testing.frontend_parent import frontend_pipeline
from test_case_generation.api_testing.backend_parent import backend_pipeline

# Define state structure
class PipelineState(TypedDict):
    figma_json: dict
    requirements_content: dict
    uiux_test_cases: list
    frontend_test_cases: list
    backend_test_cases: list

def full_pipeline(figma_json=None, requirements_content=None):

    # 1. Validate Inputs
    if not isinstance(figma_json, dict) or not figma_json or not all(key in figma_json for key in ['Layout_agent', 'Usability_agent']):
        print("❌ ERROR: Invalid or missing figma_json input or missing required keys")
        return {
            "error": "Missing or invalid figma_json input. Must contain Layout_agent and Usability_agent keys",
            "input_received": figma_json if figma_json else "No input received"
        }
    
    if not isinstance(requirements_content, dict) or not requirements_content:
        print("❌ ERROR: Invalid or missing requirements_content input")
        return {
            "error": "Missing or invalid requirements_content input",
            "input_received": requirements_content if requirements_content else "No input received"
        }

    # Log inputs for debugging
    print("✅ Received figma_json:", json.dumps(figma_json, indent=2))
    print("✅ Received requirements_content:", json.dumps(requirements_content, indent=2))

    graph = StateGraph(PipelineState)

    # 2. Define Processing Nodes
    def uiux_node(state):
        try:
            return {"uiux_test_cases": uiux_pipeline(state["figma_json"], state["requirements_content"])}
        except Exception as e:
            print("❌ UIUX Node Error:", str(e))
            return {"uiux_test_cases": [], "error": str(e)}

    def frontend_node(state):
        try:
            return {"frontend_test_cases": frontend_pipeline(state["figma_json"], state["requirements_content"])}
        except Exception as e:
            print("❌ Frontend Node Error:", str(e))
            return {"frontend_test_cases": [], "error": str(e)}

    def backend_node(state):
        try:
            return {"backend_test_cases": backend_pipeline(state["requirements_content"])}
        except Exception as e:
            print("❌ Backend Node Error:", str(e))
            return {"backend_test_cases": [], "error": str(e)}

    # 3. Add Nodes to Graph
    graph.add_node("UIUX_Testing", uiux_node)
    graph.add_node("Frontend_Testing", frontend_node)
    graph.add_node("Backend_Testing", backend_node)

    # 4. Define Execution Order
    graph.add_edge(START, "UIUX_Testing")
    graph.add_edge(START, "Frontend_Testing")
    graph.add_edge(START, "Backend_Testing")

    graph.add_edge("UIUX_Testing", END)
    graph.add_edge("Frontend_Testing", END)
    graph.add_edge("Backend_Testing", END)

    # 5. Execute Graph & Handle Results
    compiled_graph = graph.compile()
    results = compiled_graph.invoke({
        "figma_json": figma_json,
        "requirements_content": requirements_content
    })

    # Merge results safely
    test_cases = {
        "uiux_test_cases": results.get("uiux_test_cases", []),
        "frontend_test_cases": results.get("frontend_test_cases", []),
        "backend_test_cases": results.get("backend_test_cases", [])
    }

    # 6. Save Test Cases to JSON File
    file_path = os.path.join(os.getcwd(), "generated_test_cases.json")
    with open(file_path, "w") as f:
        json.dump(test_cases, f, indent=4)

    print("✅ Test cases saved at:", file_path)

    return {
        "message": "Test cases generated successfully.",
        "test_cases": test_cases,
        "file_saved": file_path
    }
