from tripmind.models.session import ConversationSession
from langchain.memory import ConversationBufferMemory
from typing import Dict, Any

class SessionManageService:
    def __init__(self):
        self.memories = {}

    def get_or_create_session(self, session_id: str) -> ConversationSession:
        """
        세션 ID로 대화 세션을 가져오거나 없으면 새로 생성
        
        Args:
            session_id: 세션 ID
                
        Returns:
            대화 세션 인스턴스
        """
        session, _ = ConversationSession.objects.get_or_create(session_id=session_id)
        return session

    def get_session_memory(self, session_id: str, memory_key: str = "chat_history") -> Dict[str, Any]:
        """세션별 메모리 가져오기"""
        if session_id not in self.memories:
            self.memories[session_id] = ConversationBufferMemory(
                memory_key=memory_key, 
                return_messages=True
            )
        return self.memories[session_id]

    def clear_memory(self, session_id: str = "default") -> bool:
        """세션 메모리 초기화"""
        if session_id in self.memories:
            del self.memories[session_id]
            return True
        return False
    
# 싱글톤 패턴 적용
session_manage_service = SessionManageService()