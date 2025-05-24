# tripmind/agents/excutors/prompt_router_agent_excutor.py
from .prompt_router_agent_graph import prompt_router_graph
from ..common.types.agent_executor_type import AgentExecutorResult, BaseAgentExcutor


class PromptRouterAgentExecutor(BaseAgentExcutor):
    """
    사용자 입력의 목적(intent)을 분류하는 에이전트 실행기
    """

    def process_prompt(
        self,
        prompt: str,
        session_id: str = "default",
        start_node: str = "input_node",
    ) -> AgentExecutorResult:
        try:
            state = {"user_input": prompt, "messages": [], "next_node": start_node}
            config = {"configurable": {"thread_id": session_id}}
            try:
                session_state = prompt_router_graph.get_state(config=config)
                if session_state and session_state.values:
                    messages = session_state.values.get("messages", [])
                    messages.append({"role": "user", "content": prompt})
                    state = {
                        **session_state.values,
                        "user_input": prompt,
                        "messages": messages,
                        "next_node": start_node,
                    }
            except:
                pass

            result = prompt_router_graph.invoke(state, config=config)
            return AgentExecutorResult(
                response=result.get("response", "응답을 생성하지 못했습니다."),
                messages=result.get("messages", []),
                context=result.get("context", {}),
                intent=result.get("intent", "unknown"),
                next_node=result.get("next_node", "unknown"),
            )

        except Exception as e:
            return {"response": f"[대화 오류] {str(e)}", "messages": [], "context": {}}
