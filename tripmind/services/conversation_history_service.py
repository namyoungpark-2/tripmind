from typing import List, Dict
from tripmind.models.session import ConversationSession, ConversationMessage

class ConversationHistoryService:
    def save_message(self, session: ConversationSession, role: str, content: str):
        """메시지 저장"""
        ConversationMessage.objects.create(session=session, role=role, content=content)
    

    def get_conversation_history(self, session: ConversationSession) -> List[Dict]:
        """대화 기록 조회"""
        try:
            messages = session.messages.all()
            return [{"role": msg.role, "content": msg.content} for msg in messages]
        except ConversationSession.DoesNotExist:
            return []

    def clear_conversation(self, session: ConversationSession) -> bool:
        """대화 기록 초기화"""
        try:
            session.messages.all().delete()
            return True
        except ConversationSession.DoesNotExist:
            return False