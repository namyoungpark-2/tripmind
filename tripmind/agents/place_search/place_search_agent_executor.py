import traceback

from tripmind.agents.place_search.types.place_search_state_type import PlaceSearchState
from .place_search_agent_graph import place_search_graph
from ..common.types.agent_executor_type import AgentExecutorResult, BaseAgentExcutor


class PlaceSearchAgentExecutor(BaseAgentExcutor):

    def process_prompt(
        self,
        prompt: str,
        session_id: str = "default",
        start_node: str = "ask_info_node",
    ) -> AgentExecutorResult:
        try:
            state = PlaceSearchState(
                user_input=prompt,
                messages=[],
                parsed_info={},
                context={"last_search": None},
                next_node=start_node,
            )

            config = {"configurable": {"thread_id": session_id}}

            try:
                session_state = place_search_graph.get_state(config=config)
                if session_state:
                    # 세션 데이터 복원
                    messages = session_state.get("messages", [])
                    messages.append({"role": "user", "content": prompt})
                    print(f"session_state: {session_state}")
                    state = PlaceSearchState(
                        messages=messages,
                        parsed_info=session_state.get("parsed_info", {}),
                        context=session_state.get("context", {}),
                        user_input=prompt,
                        next_node=start_node,
                    )
            except:
                pass

            result = place_search_graph.invoke(state, config=config)

            return AgentExecutorResult(
                response=result.get("response", "응답을 생성하지 못했습니다."),
                messages=result.get("messages", []),
                context=result.get("context", {}),
            )
        except Exception as e:
            print(traceback.format_exc())
            print(f"error: {e}")
            return {"response": f"[대화 오류] {str(e)}", "messages": [], "context": {}}
