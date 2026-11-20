# %% [markdown]
# # The agent's graph
#
# How one message moves through the agent. `build_graph` connects the steps, and `nodes.py` holds what each step does.
# Run the last cell to draw it. It shows how the steps are connected, not what is inside them, so it changes when
# you add or remove a step or an edge here. After editing this file, restart the kernel before drawing it again.
#
# **Exercise 5** is the `retrieve_memories` step: its node and its two edges.


# %%
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from backend.modules.ai.agent_workflow.nodes import agent, retrieve_memories, tools
from backend.modules.ai.agent_workflow.state import AgentState
from backend.modules.ai.agent_workflow.utils import add_cards


def build_graph():
    """
    START → retrieve_memories → agent ──→ END
                                  ↑  │ (the model asked for tools)
                                  └─ tools ←┘
    """
    return (
        StateGraph(AgentState)
        .add_node("agent", agent)
        .add_node("tools", ToolNode(tools, awrap_tool_call=add_cards))  # the tools node: runs the tools the model asked for, and adds the cards they found
        # TODO (Exercise 5): add the `retrieve_memories` node, and run it first: START → retrieve_memories → agent.
        # Then remove the edge from START to "agent" below, because retrieve_memories now leads to it.
        .add_edge(START, "agent")
        .add_conditional_edges("agent", tools_condition, ["tools", END])
        .add_edge("tools", "agent")
        .compile()
    )


# %% [markdown]
# <details>
# <summary>Show solution</summary>
#
# ```python
# def build_graph():
#     """
#     START → retrieve_memories → agent ──→ END
#                                   ↑  │ (the model asked for tools)
#                                   └─ tools ←┘
#     """
#     return (
#         StateGraph(AgentState)
#         .add_node("retrieve_memories", retrieve_memories)
#         .add_node("agent", agent)
#         .add_node("tools", ToolNode(tools, awrap_tool_call=add_cards))  # the tools node: runs the tools the model asked for, and adds the cards they found
#         .add_edge(START, "retrieve_memories")
#         .add_edge("retrieve_memories", "agent")
#         .add_conditional_edges("agent", tools_condition, ["tools", END])
#         .add_edge("tools", "agent")
#         .compile()
#     )
# ```
#
# </details>


# %% [markdown]
# ## Draw the graph


# %%
# This only runs when you run the cell here, not when the app imports this file.
if __name__ == "__main__":
    from IPython.display import Image, display

    # The picture is drawn by the mermaid.ink website, so this needs an internet connection
    display(Image(build_graph().get_graph().draw_mermaid_png()))


# %%
