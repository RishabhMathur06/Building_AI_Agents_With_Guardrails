from langgraph.graph import StateGraph, START, END

# Mock nodes (only for visualization)
def input_guardrails_node(state): return state
def planning_node(state): return state
def action_guardrails_node(state): return state
def tool_execution_node(state): return state
def response_generation_node(state): return state
def output_guardrails_node(state): return state

def generate_aegis_graph():
    """Generates and saves the Aegis architecture graph."""
    full_workflow = StateGraph(dict)

    # Add nodes
    full_workflow.add_node("Input_Guardrails", input_guardrails_node)
    full_workflow.add_node("Planning", planning_node)
    full_workflow.add_node("Action_Guardrails", action_guardrails_node)
    full_workflow.add_node("Tool_Execution", tool_execution_node)
    full_workflow.add_node("Response_Generation", response_generation_node)
    full_workflow.add_node("Output_Guardrails", output_guardrails_node)

    # Define flow
    full_workflow.add_edge(START, "Input_Guardrails")
    full_workflow.add_edge("Input_Guardrails", "Planning")
    full_workflow.add_edge("Planning", "Action_Guardrails")
    full_workflow.add_edge("Action_Guardrails", "Tool_Execution")
    full_workflow.add_edge("Tool_Execution", "Response_Generation")
    full_workflow.add_edge("Response_Generation", "Output_Guardrails")
    full_workflow.add_edge("Output_Guardrails", END)


    # Compile graph
    aegis_graph = full_workflow.compile()

    try:
        png_bytes = aegis_graph.get_graph().draw_png()
        with open("aegis_framework_graph.png", "wb") as f:
            f.write(png_bytes)

        print("✅ Aegis graph saved as 'aegis_framework_graph.png'")

    except Exception as e:
        print(f"❌ Graph generation failed: {e}")