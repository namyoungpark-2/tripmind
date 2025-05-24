from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from tripmind.agents.place_search.types.place_search_state_type import PlaceSearchState
from ..place_search.nodes.ask_info_node import ask_info_node
from ..place_search.nodes.place_search_node import (
    place_search_node,
    update_place_search_stream,
)
from ..common.nodes.node_wrapper import node_wrapper
from ..common.utils.validation_checker import should_continue_streaming


def wrap_all_nodes():
    wrapped_ask_info_node = node_wrapper(ask_info_node)
    wrapped_place_search_node = node_wrapper(place_search_node)
    wrapped_update_place_search_stream = node_wrapper(update_place_search_stream)
    return {
        "ask_info_node": wrapped_ask_info_node,
        "place_search_node": wrapped_place_search_node,
        "update_place_search_stream_node": wrapped_update_place_search_stream,
    }


# 그래프 생성
def create_place_search_agent_graph():
    memory = MemorySaver()

    graph = StateGraph(PlaceSearchState)

    wrapped_nodes = wrap_all_nodes()

    graph.add_node("ask_info_node", wrapped_nodes["ask_info_node"])
    graph.add_node("place_search_node", wrapped_nodes["place_search_node"])
    graph.add_node(
        "update_place_search_stream_node",
        wrapped_nodes["update_place_search_stream_node"],
    )

    graph.set_entry_point("ask_info_node")
    graph.add_conditional_edges(
        "ask_info_node",
        lambda state: (
            "place_search_node"
            if state.get("next_node") == "place_search_node"
            else END
        ),
    )

    graph.add_conditional_edges(
        "place_search_node",
        should_continue_streaming,
        {
            True: "update_place_search_stream_node",
            False: END,
        },
    )
    graph.add_conditional_edges(
        "update_place_search_stream_node",
        should_continue_streaming,
        {
            True: "update_place_search_stream_node",
            False: END,
        },
    )

    graph.add_edge("place_search_node", END)

    return graph.compile(checkpointer=memory)


place_search_graph = create_place_search_agent_graph()
