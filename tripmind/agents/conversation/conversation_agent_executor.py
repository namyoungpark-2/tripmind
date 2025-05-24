from .conversation_agent_graph import conversation_graph
from ..common.types.agent_executor_type import AgentExecutorResult, BaseAgentExcutor
from tripmind.services.session.session_manage_service import session_manage_service


class ConversationAgentExecutor(BaseAgentExcutor):
    def process_prompt(
        self,
        prompt: str,
        session_id: str = "default",
        start_node: str = "greeting_node",
    ):
        try:
            state, config = session_manage_service.get_session_state_and_config(
                conversation_graph, prompt, start_node, session_id
            )

            for result in conversation_graph.stream(state, config=config):
                if result:
                    for node_name, node_state in result.items():
                        state.update(node_state)
                        yield AgentExecutorResult(
                            response=node_state.get("response", ""),
                            messages=node_state.get("messages", []),
                            context=node_state.get("context", {}),
                            streaming=node_state.get("streaming", {}),
                        )
        except Exception as e:
            yield AgentExecutorResult(
                response=f"[대화 오류] {str(e)}",
                messages=[],
                context={},
                streaming={},
            )
