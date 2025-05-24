from tripmind.models.session import ConversationSession
from langchain.memory import ConversationBufferMemory
from typing import Dict, Any
from langgraph.graph import StateGraph
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage


class SessionManageService:
    def __init__(self):
        self.memories = {}

    # 추후 세션 / 사용자 별 session을 저장하여 과거 대화 목록 등을 조회할 수 있도록 할 예정
    def get_or_create_session(self, session_id: str) -> ConversationSession:
        session, _ = ConversationSession.objects.get_or_create(session_id=session_id)
        return session

    def get_session_memory(
        self,
        session_id: str,
        memory_key: str = "chat_history",
        input_key: str = "input",
        output_key: str = "output",
    ) -> Dict[str, Any]:
        if session_id not in self.memories:
            self.memories[session_id] = ConversationBufferMemory(
                memory_key=memory_key,
                return_messages=True,
                input_key=input_key,
                output_key=output_key,
            )
        return self.memories[session_id]

    def clear_memory(self, session_id: str = "default") -> bool:
        if session_id in self.memories:
            del self.memories[session_id]
            return True
        return False

    def get_session_state_and_config(
        self,
        graph: StateGraph,
        prompt: str,
        start_node: str,
        session_id: str = "default",
    ) -> tuple[dict, dict]:
        state = {"user_input": prompt, "messages": [], "next_node": start_node}
        config = {"configurable": {"thread_id": session_id}}

        try:
            messages = state.get("messages", [])
            messages.append({"role": "user", "content": prompt})
            session_state = graph.get_state(config=config)
            if session_state:
                state = {
                    **session_state,
                    "config_data": config,
                    "user_input": prompt,
                    "messages": messages,
                    "next_node": start_node,
                }
        except:
            pass
        return state, config

    def _convert_messages_to_dicts(messages: list[BaseMessage]) -> list[dict]:
        formatted = []
        for m in messages:
            role = (
                "user"
                if isinstance(m, HumanMessage)
                else (
                    "assistant"
                    if isinstance(m, AIMessage)
                    else "system" if isinstance(m, SystemMessage) else "function"
                )
            )
            formatted.append({"role": role, "content": m.content})
        return formatted


session_manage_service = SessionManageService()
