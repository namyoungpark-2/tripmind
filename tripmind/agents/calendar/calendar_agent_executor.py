from .types.calendar_state_type import CalendarState
from ..common.types.agent_executor_type import AgentExecutorResult, BaseAgentExcutor
from tripmind.services.session.session_manage_service import session_manage_service
from .calendar_agent_graph import calendar_agent_graph


class CalendarRouterAgentExecutor(BaseAgentExcutor):
    def process_prompt(
        self,
        prompt: str,
        session_id: str = "default",
        start_node: str = "input_node",
    ):
        try:
            state, config = session_manage_service.get_session_state_and_config(
                calendar_agent_graph, prompt, start_node, session_id
            )

            calendar_agent_state = CalendarState(**state)

            for result in calendar_agent_graph.stream(
                calendar_agent_state, config=config
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
