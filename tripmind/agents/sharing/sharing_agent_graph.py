from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from tripmind.agents.sharing.types.sharing_state_type import SharingRouterState
from tripmind.agents.sharing.nodes.sharing_node import sharing_node
from tripmind.agents.common.nodes.node_wrapper import node_wrapper


def wrap_all_nodes():
    wrapped_sharing_node = node_wrapper(sharing_node)

    return {
        "sharing_node": wrapped_sharing_node,
    }


def create_sharing_agent_graph():
    memory = MemorySaver()

    graph = StateGraph(SharingRouterState)

    wrapped_nodes = wrap_all_nodes()

    graph.add_node("sharing_node", wrapped_nodes["sharing_node"])

    graph.set_entry_point("sharing_node")

    graph.add_edge("sharing_node", END)

    return graph.compile(checkpointer=memory)


sharing_agent_graph = create_sharing_agent_graph()
