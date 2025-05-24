from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .nodes.router_node import router_node
from .nodes.greeting_node import greeting_node, update_greeting_stream
from .nodes.conversation_node import conversation_node, update_conversation_stream
from .types.conversation_state_type import ConversationState
from ..common.nodes.node_wrapper import node_wrapper
from tripmind.clients.llm.claude_client import claude_client
from ..common.utils.validation_checker import should_continue_streaming


def wrap_all_nodes():
    wrapped_router_node = node_wrapper(router_node)
    wrapped_greeting_node = node_wrapper(greeting_node)
    wrapped_conversation_node = node_wrapper(conversation_node)
    wrapped_update_greeting_stream = node_wrapper(update_greeting_stream)
    wrapped_update_conversation_stream = node_wrapper(update_conversation_stream)
    return {
        "router_node": wrapped_router_node,
        "greeting_node": wrapped_greeting_node,
        "conversation_node": wrapped_conversation_node,
        "update_greeting_stream_node": wrapped_update_greeting_stream,
        "update_conversation_stream_node": wrapped_update_conversation_stream,
    }


def create_conversation_agent_graph():
    memory = MemorySaver()
    graph = StateGraph(ConversationState)
    wrapped_nodes = wrap_all_nodes()

    graph.add_node("router_node", wrapped_nodes["router_node"])
    graph.add_node("greeting_node", wrapped_nodes["greeting_node"])
    graph.add_node(
        "conversation_node",
        lambda state: wrapped_nodes["conversation_node"](claude_client, state),
    )
    graph.add_node(
        "update_greeting_stream_node", wrapped_nodes["update_greeting_stream_node"]
    )
    graph.add_node(
        "update_conversation_stream_node",
        wrapped_nodes["update_conversation_stream_node"],
    )

    graph.set_entry_point("router_node")

    graph.add_conditional_edges(
        "router_node",
        lambda state: state["next_node"],
        {
            "greeting_node": "greeting_node",
            "conversation_node": "conversation_node",
        },
    )
    graph.add_conditional_edges(
        "greeting_node",
        should_continue_streaming,
        {
            True: "update_greeting_stream_node",
            False: END,
        },
    )
    graph.add_conditional_edges(
        "update_greeting_stream_node",
        should_continue_streaming,
        {
            True: "update_greeting_stream_node",
            False: END,
        },
    )
    graph.add_conditional_edges(
        "conversation_node",
        should_continue_streaming,
        {
            True: "update_conversation_stream_node",
            False: END,
        },
    )
    graph.add_conditional_edges(
        "update_conversation_stream_node",
        should_continue_streaming,
        {
            True: "update_conversation_stream_node",
            False: END,
        },
    )
    graph.add_edge("conversation_node", END)

    return graph.compile(checkpointer=memory)


conversation_graph = create_conversation_agent_graph()
