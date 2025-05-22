from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tripmind.services.session_manage_service import SessionManageService
from tripmind.services.conversation_history_service import ConversationHistoryService

class ConversationHistoryAPIView(APIView):
    """대화 기록 관리 API"""
    
    def get(self, request, *args, **kwargs):
        session_id = request.session.session_key or "default"
        session_manage_service = SessionManageService()
        session = session_manage_service.get_session(session_id)
        conversation_history_service = ConversationHistoryService()
        history = conversation_history_service.get_conversation_history(session)
        return Response({"history": history}, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        session_id = request.session.session_key or "default"
        session_manage_service = SessionManageService()
        session = session_manage_service.get_session(session_id)
        conversation_history_service = ConversationHistoryService()
        success = conversation_history_service.clear_conversation(session)
        if success:
            return Response({"message": "대화 기록이 초기화되었습니다."}, status=status.HTTP_200_OK)
        return Response({"error": "대화 기록 초기화에 실패했습니다."}, status=status.HTTP_404_NOT_FOUND)