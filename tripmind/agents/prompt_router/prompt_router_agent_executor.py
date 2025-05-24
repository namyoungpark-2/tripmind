from .prompt_router_agent_graph import prompt_router_graph
from .types.prompt_router_state_type import PromptRouterState
from ..common.types.agent_executor_type import AgentExecutorResult, BaseAgentExcutor
from tripmind.services.session.session_manage_service import session_manage_service


class PromptRouterAgentExecutor(BaseAgentExcutor):
    def process_prompt(
        self,
        prompt: str,
        session_id: str = "default",
        start_node: str = "input_node",
    ) -> AgentExecutorResult:
        try:
            state, config = session_manage_service.get_session_state_and_config(
                prompt_router_graph, prompt, start_node, session_id
            )

            prompt_router_state = PromptRouterState(**state)

            result: PromptRouterState = prompt_router_graph.invoke(
                prompt_router_state, config=config
            )

            return AgentExecutorResult(
                response=result.get("response", "응답을 생성하지 못했습니다."),
                messages=result.get("messages", []),
                context=result.get("context", {}),
                intent=result.get("intent", "unknown"),
                next_node=result.get("next_node", "unknown"),
                streaming=result.get("streaming", {}),
            )

        except Exception as e:
            return {"response": f"[대화 오류] {str(e)}", "messages": [], "context": {}}
