from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .nodes.router_node import router_node
from .nodes.greeting_node import greeting_node
from .nodes.conversation_node import conversation_node
from .types.conversation_state_type import ConversationState
from ..common.nodes.node_wrapper import node_wrapper
from tripmind.clients.llm.claude_client import claude_client

# 이후 일상 대화에 필요한 여러 도구들 추가 (ex: 장소 검색, 날씨 정보, 뉴스 등)


def wrap_all_nodes():
    """모든 노드에 검증 래퍼 적용"""
    wrapped_router_node = node_wrapper(router_node)
    wrapped_greeting_node = node_wrapper(greeting_node)
    wrapped_conversation_node = node_wrapper(conversation_node)

    return {
        "router_node": wrapped_router_node,
        "greeting_node": wrapped_greeting_node,
        "conversation_node": wrapped_conversation_node,
    }


# 그래프 생성
def create_conversation_agent_graph():
    """여행 일정 에이전트 그래프 생성"""
    # 체크포인트 저장소
    memory = MemorySaver()

    # 그래프 초기화
    graph = StateGraph(ConversationState)

    # 래핑된 노드 가져오기
    wrapped_nodes = wrap_all_nodes()

    # 노드 추가
    graph.add_node("router", wrapped_nodes["router_node"])
    graph.add_node("greeting", wrapped_nodes["greeting_node"])
    graph.add_node(
        "conversation",
        lambda state: wrapped_nodes["conversation_node"](claude_client, state),
    )

    # 시작 노드 설정
    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",  # 라우터 노드
        lambda state: state["next_node"],
        {
            "greeting": "greeting",
            "conversation": "conversation",
        },
    )

    # 응답 노드에서 종료
    graph.add_edge("greeting", END)
    graph.add_edge("conversation", END)

    # 컴파일
    return graph.compile(checkpointer=memory)


# 그래프 인스턴스 생성
conversation_graph = create_conversation_agent_graph()
