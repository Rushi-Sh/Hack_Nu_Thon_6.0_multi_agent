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
    """
    Multi-agent pipeline for generating test cases from Figma JSON and requirements content.
    Returns structured test cases for UI/UX, frontend, and backend testing.
    """
    if not figma_json or not isinstance(figma_json, dict):
        return {"error": "Missing or invalid figma_json input", "input_received": figma_json}
    
    if not requirements_content or not isinstance(requirements_content, dict):
        return {"error": "Missing or invalid requirements_content input", "input_received": requirements_content}
    
    graph = StateGraph(PipelineState)

    # Node: Generate UI/UX test cases
    def uiux_node(state):
        return {"uiux_test_cases": uiux_pipeline(state["figma_json"], state["requirements_content"])}

    # Node: Generate Frontend test cases
    def frontend_node(state):
        return {"frontend_test_cases": frontend_pipeline(state["figma_json"], state["requirements_content"])}

    # Node: Generate Backend test cases
    def backend_node(state):
        return {"backend_test_cases": backend_pipeline(state["requirements_content"])}

    graph.add_node("UIUX_Testing", uiux_node)
    graph.add_node("Frontend_Testing", frontend_node)
    graph.add_node("Backend_Testing", backend_node)

    # Define execution order (parallel execution)
    graph.add_edge(START, "UIUX_Testing")
    graph.add_edge(START, "Frontend_Testing")
    graph.add_edge(START, "Backend_Testing")
    
    graph.add_edge("UIUX_Testing", END)
    graph.add_edge("Frontend_Testing", END)
    graph.add_edge("Backend_Testing", END)

    # Execute the pipeline
    compiled_graph = graph.compile()
    results = compiled_graph.invoke({
        "figma_json": figma_json,
        "requirements_content": requirements_content
    })

    # Save the test cases to a JSON file
    test_cases = {
        "uiux_test_cases": results.get("uiux_test_cases", []),
        "frontend_test_cases": results.get("frontend_test_cases", []),
        "backend_test_cases": results.get("backend_test_cases", [])
    }

    file_path = os.path.join(os.getcwd(), "generated_test_cases.json")
    with open(file_path, "w") as f:
        json.dump(test_cases, f, indent=4)

    return {
        "message": "Test cases generated successfully.",
        "test_cases": test_cases,
        "file_saved": file_path
    }