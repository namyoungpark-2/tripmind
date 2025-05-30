from .types.sharing_state_type import SharingRouterState
from ..common.types.agent_executor_type import AgentExecutorResult, BaseAgentExcutor
from tripmind.services.session.session_manage_service import session_manage_service
from .sharing_agent_graph import sharing_agent_graph


class SharingRouterAgentExecutor(BaseAgentExcutor):
    def process_prompt(
        self,
        prompt: str,
        session_id: str = "default",
        start_node: str = "input_node",
    ):
        try:
            state, config = session_manage_service.get_session_state_and_config(
                sharing_agent_graph, prompt, start_node, session_id
            )

            sharing_agent_state = SharingRouterState(**state)

            for result in sharing_agent_graph.stream(
                sharing_agent_state, config=config
            ):
                if result:
                    for node_name, node_state in result.items():
                        state.update(node_state)
                        yield AgentExecutorResult(
                            response=node_state.get(
                                "response", "응답을 생성하지 못했습니다."
                            ),
                            messages=node_state.get("messages", []),
                            context=node_state.get("context", {}),
                            intent=node_state.get("intent", "unknown"),
                            next_node=node_state.get("next_node", "unknown"),
                            streaming=node_state.get("streaming", {}),
                        )

        except Exception as e:
            return {"response": f"[대화 오류] {str(e)}", "messages": [], "context": {}}
