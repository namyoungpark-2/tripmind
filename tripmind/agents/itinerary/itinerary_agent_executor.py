from tripmind.agents.itinerary.itinerary_agent_graph import itinerary_graph
from tripmind.agents.itinerary.types.itinerary_state_type import ItineraryState
from tripmind.agents.common.types.agent_executor_type import (
    AgentExecutorResult,
    BaseAgentExcutor,
)


class ItineraryAgentExecutor(BaseAgentExcutor):
    """여행 일정 에이전트 실행기"""

    def process_prompt(
        self,
        prompt: str,
        session_id: str = "default",
        start_node: str = "ask_info_node",
    ) -> AgentExecutorResult:
        try:
            state: ItineraryState = {
                "user_input": prompt,
                "messages": [],
                "next_node": start_node,
            }
            config = {
                "configurable": {
                    "thread_id": session_id,
                }
            }

            try:

                session_state = itinerary_graph.get_state(config=config)
                if session_state:
                    messages = session_state.get("messages", [])
                    messages.append({"role": "user", "content": prompt})
                    state = {
                        **session_state,
                        "user_input": prompt,
                        "messages": messages,
                        "next_node": start_node,
                    }

            except:
                pass

            result = itinerary_graph.invoke(state, config=config)

            return AgentExecutorResult(
                response=result.get("response", "응답을 생성하지 못했습니다."),
                messages=result.get("messages", []),
                context=result.get("context", {}),
            )
        except Exception as e:
            import traceback

            traceback.print_exc()
            return AgentExecutorResult(
                response=f"[여행 일정 생성 오류] {str(e)}",
                messages=[],
                context={},
            )
