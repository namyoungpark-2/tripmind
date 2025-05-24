from tripmind.agents.itinerary.itinerary_agent_graph import itinerary_graph
from tripmind.agents.common.types.agent_executor_type import (
    AgentExecutorResult,
    BaseAgentExcutor,
)
from tripmind.services.session.session_manage_service import session_manage_service
import traceback


class ItineraryAgentExecutor(BaseAgentExcutor):
    def process_prompt(
        self,
        prompt: str,
        session_id: str = "default",
        start_node: str = "ask_info_node",
    ):
        try:
            state, config = session_manage_service.get_session_state_and_config(
                itinerary_graph, prompt, start_node, session_id
            )

            for result in itinerary_graph.stream(
                state, config={**config, "recursion_limit": 150}
            ):
                if result:
                    for _, node_state in result.items():
                        state.update(node_state)
                        yield AgentExecutorResult(
                            response=node_state.get("response", ""),
                            messages=node_state.get("messages", []),
                            context=node_state.get("context", {}),
                            intent=node_state.get("intent", ""),
                            next_node=node_state.get("next_node", ""),
                            streaming=node_state.get("streaming", {}),
                        )
        except Exception as e:
            traceback.print_exc()
            yield AgentExecutorResult(
                response=f"[여행 일정 생성 오류] {str(e)}",
                messages=[],
                context={},
            )
