from .conversation_agent_graph import conversation_graph
from ..common.types.agent_executor_type import AgentExecutorResult, BaseAgentExcutor


class ConversationAgentExecutor(BaseAgentExcutor):
    def process_prompt(
        self,
        prompt: str,
        session_id: str = "default",
        start_node: str = "greeting_node",
    ) -> AgentExecutorResult:
        try:
            state = {"user_input": prompt, "messages": [], "next_node": start_node}
            config = {"configurable": {"thread_id": session_id}}

            try:
                session_state = conversation_graph.get_state(config=config)
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

            result = conversation_graph.invoke(state, config=config)

            return AgentExecutorResult(
                response=result.get("response", "응답을 생성하지 못했습니다."),
                messages=result.get("messages", []),
                context=result.get("context", {}),
            )
        except Exception as e:
            return AgentExecutorResult(
                response=f"[대화 오류] {str(e)}",
                messages=[],
                context={},
            )
