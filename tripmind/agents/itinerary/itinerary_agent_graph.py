from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .types.itinerary_state_type import ItineraryState
from .nodes.itinerary_node import itinerary_node
from .nodes.ask_info_node import ask_info_node
from .nodes.place_search_node import place_search_node
from .nodes.calendar_node import calendar_node
from .nodes.sharing_node import sharing_node
from tripmind.agents.common.node.node_wrapper import node_wrapper
from .itinerary_agent_llm import itinerary_agent_llm


def wrap_all_nodes():
    wrapped_itinerary_node = node_wrapper(itinerary_node)
    wrapped_ask_info_node = node_wrapper(ask_info_node)
    wrapped_place_search_node = node_wrapper(place_search_node)
    wrapped_calendar_node = node_wrapper(calendar_node)
    wrapped_sharing_node = node_wrapper(sharing_node)

    return {
        "itinerary_node": wrapped_itinerary_node,
        "ask_info_node": wrapped_ask_info_node,
        "place_search_node": wrapped_place_search_node,
        "calendar_node": wrapped_calendar_node,
        "sharing_node": wrapped_sharing_node,
    }


# 그래프 생성
def create_itinerary_agent_graph():
    # 체크포인트 저장소
    memory = MemorySaver()

    # 그래프 초기화
    graph = StateGraph(ItineraryState)

    # 래핑된 노드 가져오기
    wrapped_nodes = wrap_all_nodes()

    # 노드 추가
    graph.add_node(
        "itinerary",
        lambda state: wrapped_nodes["itinerary_node"](
            itinerary_agent_llm.get_llm(), state
        ),
    )
    graph.add_node("ask_info", wrapped_nodes["ask_info_node"])
    graph.add_node(
        "sharing",
        lambda state: wrapped_nodes["sharing_node"](
            itinerary_agent_llm.get_llm(), state
        ),
    )
    graph.add_node(
        "place_search",
        lambda state: wrapped_nodes["place_search_node"](
            itinerary_agent_llm.get_llm(), state
        ),
    )
    graph.add_node(
        "calendar",
        lambda state: wrapped_nodes["calendar_node"](
            itinerary_agent_llm.get_llm(), state
        ),
    )

    # 시작 노드 설정
    graph.set_entry_point("itinerary")

    # 라우터 노드 조건부 전환: next_node 필드를 기반으로 각 노드로 라우팅
    graph.add_conditional_edges(
        "itinerary",
        lambda state: state["next_node"],  # next_node 필드 사용
        {
            "ask_info": "ask_info",
            "place_search": "place_search",
            "calendar": "calendar",
            "sharing": "sharing",
            "itinerary": END,
            "end": END,
        },
    )

    # 응답 노드에서 종료
    graph.add_edge("itinerary", END)
    graph.add_edge("ask_info", END)
    graph.add_edge("place_search", END)
    graph.add_edge("calendar", END)
    graph.add_edge("sharing", END)

    # 컴파일
    return graph.compile(checkpointer=memory)


# 그래프 인스턴스 생성
itinerary_graph = create_itinerary_agent_graph()
