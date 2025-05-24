from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from tripmind.agents.place_search.types.place_search_state_type import PlaceSearchState
from ..place_search.nodes.ask_info_node import ask_info_node
from ..place_search.nodes.place_search_node import place_search_node
from ..common.nodes.node_wrapper import node_wrapper


def wrap_all_nodes():
    wrapped_ask_info_node = node_wrapper(ask_info_node)
    wrapped_place_search_node = node_wrapper(place_search_node)

    return {
        "place_search": wrapped_ask_info_node,
        "place_search_node": wrapped_place_search_node,
    }


# 그래프 생성
def create_place_search_agent_graph():
    memory = MemorySaver()

    graph = StateGraph(PlaceSearchState)

    wrapped_nodes = wrap_all_nodes()

    graph.add_node("place_search", wrapped_nodes["place_search"])
    graph.add_node("place_search_node", wrapped_nodes["place_search_node"])

    graph.set_entry_point("place_search")

    graph.add_edge("place_search", "place_search_node")
    graph.add_edge("place_search_node", END)

    return graph.compile(checkpointer=memory)


place_search_graph = create_place_search_agent_graph()
