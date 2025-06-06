from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from tripmind.agents.itinerary.nodes.ask_info_node import ask_info_node
from .types.itinerary_state_type import ItineraryState
from .nodes.itinerary_node import itinerary_node, update_itinerary_stream
from tripmind.agents.common.nodes.node_wrapper import node_wrapper
from tripmind.clients.llm.claude_client import claude_client
from ..common.utils.validation_checker import should_continue_streaming
from .nodes.itinerary_list_node import itinerary_list_node
from .nodes.router_node import router_node


def wrap_all_nodes():
    wrapped_itinerary_node = node_wrapper(
        lambda state: itinerary_node(claude_client, state)
    )
    wrapped_ask_info_node = node_wrapper(ask_info_node)
    wrapped_update_itinerary_stream = node_wrapper(update_itinerary_stream)
    wrapped_itinerary_list_node = node_wrapper(itinerary_list_node)
    wrapped_router_node = node_wrapper(router_node)
    return {
        "itinerary_node": wrapped_itinerary_node,
        "update_itinerary_stream_node": wrapped_update_itinerary_stream,
        "ask_info_node": wrapped_ask_info_node,
        "itinerary_list_node": wrapped_itinerary_list_node,
        "router_node": wrapped_router_node,
    }


def create_itinerary_agent_graph():
    memory = MemorySaver()

    graph = StateGraph(ItineraryState)

    wrapped_nodes = wrap_all_nodes()

    graph.add_node("itinerary_node", wrapped_nodes["itinerary_node"])
    graph.add_node(
        "update_itinerary_stream_node", wrapped_nodes["update_itinerary_stream_node"]
    )
    graph.add_node("ask_info_node", wrapped_nodes["ask_info_node"])
    graph.add_node("itinerary_list_node", wrapped_nodes["itinerary_list_node"])
    graph.add_node("router_node", wrapped_nodes["router_node"])

    graph.set_entry_point("router_node")

    graph.add_conditional_edges(
        "router_node",
        lambda state: (
            "itinerary_list_node"
            if state["next_node"] == "itinerary_list_node"
            else "ask_info_node"
        ),
    )

    graph.add_conditional_edges(
        "ask_info_node",
        lambda state: (
            END if state["next_node"] == "ask_info_node" else "itinerary_node"
        ),
    )

    graph.add_conditional_edges(
        "itinerary_node",
        should_continue_streaming,
        {
            True: "update_itinerary_stream_node",
            False: END,
        },
    )

    graph.add_conditional_edges(
        "update_itinerary_stream_node",
        should_continue_streaming,
        {
            True: "update_itinerary_stream_node",
            False: END,
        },
    )
    graph.add_edge("itinerary_list_node", END)
    return graph.compile(checkpointer=memory)


itinerary_graph = create_itinerary_agent_graph()
