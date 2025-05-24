from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from tripmind.clients.llm.claude_client import claude_client
from tripmind.agents.prompt_router.types.prompt_router_state_type import (
    PromptRouterState,
)
from tripmind.agents.prompt_router.nodes.input_node import input_node
from tripmind.agents.prompt_router.nodes.classify_intent_node import (
    classify_intent_node,
)
from tripmind.agents.common.nodes.node_wrapper import node_wrapper


def wrap_all_nodes():
    wrapped_input_node = node_wrapper(input_node)
    wrapped_classify_intent_node = node_wrapper(
        lambda state: classify_intent_node(claude_client, state)
    )

    return {
        "input_node": wrapped_input_node,
        "classify_intent_node": wrapped_classify_intent_node,
    }


# 그래프 생성
def create_prompt_router_agent_graph():
    memory = MemorySaver()

    graph = StateGraph(PromptRouterState)

    wrapped_nodes = wrap_all_nodes()

    graph.add_node("input_node", wrapped_nodes["input_node"])
    graph.add_node("classify_intent_node", wrapped_nodes["classify_intent_node"])

    graph.set_entry_point("input_node")

    graph.add_conditional_edges(
        "input_node",
        lambda state: (
            "classify_intent_node"
            if state.get("next_node") == "classify_intent_node"
            else END
        ),
    )
    graph.add_edge("classify_intent_node", END)

    # 컴파일
    return graph.compile(checkpointer=memory)


# 그래프 인스턴스 생성
prompt_router_graph = create_prompt_router_agent_graph()
