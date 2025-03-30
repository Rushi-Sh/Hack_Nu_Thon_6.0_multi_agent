import langgraph
from langchain.agents import AgentExecutor
from langgraph.graph import Graph, START, END
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import testing pipelines
from test_case_generation.visual_testing.ui_ux_parent import uiux_pipeline
from test_case_generation.frontend_testing.frontend_parent import frontend_pipeline
from test_case_generation.api_testing.backend_parent import backend_pipeline

def full_pipeline(figma_json, website_content, requirements_content):
    """
    Executes a full automated testing pipeline across UI/UX, frontend, and backend.
    """

    graph = Graph()

    # Add nodes for different testing stages
    # Wrap pipeline functions to ensure correct parameter passing
    graph.add_node("UIUX_Testing", lambda state: uiux_pipeline(state["figma_json"], state["website_content"], state["requirements_content"]))
    graph.add_node("Frontend_Testing", lambda state: frontend_pipeline(state["website_content"], state["requirements_content"], state["figma_json"]))
    graph.add_node("Backend_Testing", lambda state: backend_pipeline(state["requirements_content"]))

    # Define execution order
    graph.add_edge(START, "UIUX_Testing")
    graph.add_edge("UIUX_Testing", "Frontend_Testing")
    graph.add_edge("Frontend_Testing", "Backend_Testing")
    graph.add_edge("Backend_Testing", END)

    # Execute the pipeline
    # Create a compiled graph that can be executed
    compiled_graph = graph.compile()
    return compiled_graph.invoke({
        "figma_json": figma_json,
        "website_content": website_content,
        "requirements_content": requirements_content
    })
