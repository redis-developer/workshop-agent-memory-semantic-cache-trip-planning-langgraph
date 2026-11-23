# %% [markdown]
# # The agent's graph
#
# How one message moves through the agent. `build_graph` connects the steps, and `nodes.py` holds what each step does.
# Run the last cell to draw it. It shows how the steps are connected, not what is inside them, so it changes when
# you add or remove a step or an edge here. After editing this file, restart the kernel before drawing it again.
#
# - **Exercise 5 (solved):** the `retrieve_memories` step: its node and its two edges.
# - **Exercise 6B (solved):** the `check_cache` step, and the edge that ends the graph on a hit.
# - **Exercise 7B (solved):** the `store_in_cache` step, after the agent.


# %%
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from backend.modules.ai.agent_workflow.nodes import agent, check_cache, retrieve_memories, store_in_cache, tools
from backend.modules.ai.agent_workflow.state import AgentState
from backend.modules.ai.agent_workflow.tools.middleware import process_tool_call


def build_graph():
    """
    START → check_cache ──→ END (a similar question was answered before)
                │
                └→ retrieve_memories → agent ──→ store_in_cache → END
                                         ↑  │ (the model asked for tools)
                                         └─ tools ←┘
    """
    return (
        StateGraph(AgentState)
        .add_node("check_cache", check_cache)  # Exercise 6B (solved)
        .add_node("retrieve_memories", retrieve_memories)  # Exercise 5 (solved)
        .add_node("agent", agent)
        .add_node("store_in_cache", store_in_cache)  # Exercise 7B (solved)
        .add_node("tools", ToolNode(tools, awrap_tool_call=process_tool_call))  # the tools node: runs the tools the model asked for, and adds the cards they found
        .add_edge(START, "check_cache")  # Exercise 6B (solved)
        .add_conditional_edges("check_cache", lambda state: END if state["is_cache_hit"] else "retrieve_memories", ["retrieve_memories", END])  # Exercise 6B (solved)
        .add_edge("retrieve_memories", "agent")  # Exercise 5 (solved)
        .add_conditional_edges("agent", tools_condition, {"tools": "tools", END: "store_in_cache"})  # Exercise 7B (solved)
        .add_edge("store_in_cache", END)  # Exercise 7B (solved)
        .add_edge("tools", "agent")
        .compile()
    )


# %% [markdown]
# ## Draw the graph


# %%
# This only runs when you run the cell here, not when the app imports this file.
if __name__ == "__main__":
    from IPython.display import Image, display

    # The picture is drawn by the mermaid.ink website, so this needs an internet connection
    display(Image(build_graph().get_graph().draw_mermaid_png()))


# %%
