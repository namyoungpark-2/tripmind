import os

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .types.travel_agent_state_type import TravelAgentState
from .nodes.input_node import input_node
from .nodes.router_node import router_node
from .nodes.internal.itinerary_node import itinerary_node
from .nodes.greeting_node import greeting_node
from .nodes.ask_info_node import ask_info_node
from .nodes.external.place_search_node import place_search_node
from .nodes.external.calendar_node import calendar_node
from .nodes.internal.conversation_node import conversation_node
from langchain_anthropic import ChatAnthropic
from .nodes.external.sharing_node import sharing_node
from .nodes.node_wrapper import node_wrapper


def get_llm():
    """Claude 모델 초기화"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다.")
    return ChatAnthropic(model="claude-3-opus-20240229", anthropic_api_key=api_key)


# 노드 래핑 함수
def wrap_all_nodes():
    """모든 노드에 검증 래퍼 적용"""
    wrapped_input_node = node_wrapper(input_node)
    wrapped_router_node = node_wrapper(router_node)
    wrapped_itinerary_node = node_wrapper(itinerary_node)
    wrapped_greeting_node = node_wrapper(greeting_node)
    wrapped_ask_info_node = node_wrapper(ask_info_node)
    wrapped_place_search_node = node_wrapper(place_search_node)
    wrapped_calendar_node = node_wrapper(calendar_node)
    wrapped_conversation_node = node_wrapper(conversation_node)
    wrapped_sharing_node = node_wrapper(sharing_node)

    return {
        "input_node": wrapped_input_node,
        "router_node": wrapped_router_node,
        "itinerary_node": wrapped_itinerary_node,
        "greeting_node": wrapped_greeting_node,
        "ask_info_node": wrapped_ask_info_node,
        "place_search_node": wrapped_place_search_node,
        "calendar_node": wrapped_calendar_node,
        "conversation_node": wrapped_conversation_node,
        "sharing_node": wrapped_sharing_node,
    }


# LLM 인스턴스 생성
llm = get_llm()


# 그래프 생성
def create_itinerary_agent_graph():
    """여행 일정 에이전트 그래프 생성"""
    # 체크포인트 저장소
    memory = MemorySaver()

    # 그래프 초기화
    graph = StateGraph(TravelAgentState)

    # 래핑된 노드 가져오기
    wrapped_nodes = wrap_all_nodes()

    # 노드 추가
    graph.add_node("input", wrapped_nodes["input_node"])
    graph.add_node("router", wrapped_nodes["router_node"])
    graph.add_node(
        "itinerary", lambda state: wrapped_nodes["itinerary_node"](llm, state)
    )
    graph.add_node("greeting", wrapped_nodes["greeting_node"])
    graph.add_node("ask_info", wrapped_nodes["ask_info_node"])
    graph.add_node("sharing", lambda state: wrapped_nodes["sharing_node"](llm, state))
    graph.add_node(
        "place_search", lambda state: wrapped_nodes["place_search_node"](llm, state)
    )
    graph.add_node("calendar", lambda state: wrapped_nodes["calendar_node"](llm, state))
    graph.add_node(
        "conversation", lambda state: wrapped_nodes["conversation_node"](llm, state)
    )

    # 시작 노드 설정
    graph.set_entry_point("input")

    # 엣지 추가: input_node에서 모든 분석을 마치고 바로 router_node로 이동
    graph.add_edge("input", "router")

    # 라우터 노드 조건부 전환: next_node 필드를 기반으로 각 노드로 라우팅
    graph.add_conditional_edges(
        "router",
        lambda state: state["next_node"],  # next_node 필드 사용
        {
            "greeting": "greeting",
            "itinerary": "itinerary",
            "ask_info": "ask_info",
            "place_search": "place_search",
            "calendar": "calendar",
            "conversation": "conversation",
            "sharing": "sharing",
            "end": END,
        },
    )

    # 응답 노드에서 종료
    graph.add_edge("greeting", END)
    graph.add_edge("itinerary", END)
    graph.add_edge("ask_info", END)
    graph.add_edge("place_search", END)
    graph.add_edge("calendar", END)
    graph.add_edge("conversation", END)
    graph.add_edge("sharing", END)

    # 컴파일
    return graph.compile(checkpointer=memory)


# 그래프 인스턴스 생성
itinerary_graph = create_itinerary_agent_graph()


def run_travel_agent(user_input: str, session_id: str = None, state=None):
    """
    여행 에이전트 실행

    Args:
        user_input: 사용자 입력
        session_id: 세션 ID
        state: 이전 상태 (없으면 새로 생성)

    Returns:
        업데이트된 상태, 에이전트 응답
    """
    # 그래프 생성
    graph = create_itinerary_agent_graph()

    # 초기 상태 설정
    if state is None:
        # 상태 직접 생성
        state = {
            "messages": [],
            "query": user_input,
            "current_agent": None,
            "destination": None,
            "duration": None,
            "travelers": None,
            "budget": None,
            "preferences": None,
            "special_requirements": None,
            "search_results": None,
            "itinerary_plan": None,
            "session_id": session_id or "default",
        }
    else:
        state["query"] = user_input

    # 그래프 실행
    state = graph.invoke(state)

    # 에이전트 응답 (마지막 assistant 메시지)
    assistant_messages = [
        msg for msg in state["messages"] if msg["role"] == "assistant"
    ]

    response = assistant_messages[-1]["content"] if assistant_messages else ""

    return state, response
