from tripmind.agents.place_search.types.place_search_state_type import PlaceSearchState
from .place_search_agent_graph import place_search_graph
from ..common.types.agent_executor_type import AgentExecutorResult, BaseAgentExcutor
from tripmind.services.session.session_manage_service import session_manage_service


class PlaceSearchAgentExecutor(BaseAgentExcutor):
    def process_prompt(
        self,
        prompt: str,
        session_id: str = "default",
        start_node: str = "ask_info_node",
    ):
        try:
            state, config = session_manage_service.get_session_state_and_config(
                place_search_graph, prompt, start_node, session_id
            )

            place_search_state = PlaceSearchState(**state)

            for result in place_search_graph.stream(
                place_search_state, config={**config, "recursion_limit": 100}
            ):
                if result:
                    for _, node_state in result.items():
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
