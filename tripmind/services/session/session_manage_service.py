from tripmind.models.session import ConversationSession
from langchain.memory import ConversationBufferMemory
from typing import Dict, Any


class SessionManageService:
    def __init__(self):
        self.memories = {}

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


session_manage_service = SessionManageService()
