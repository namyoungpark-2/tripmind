from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tripmind.agents.excutors.itinerary_agent_excutor import ItineraryAgentExecutor
from tripmind.api.serializers.itinerary_serializer import MessageSerializer
from tripmind.services.langgraph_service import LangGraphService
from tripmind.services.session_manage_service import SessionManageService
from tripmind.services.conversation_history_service import ConversationHistoryService

class LangGraphAPIView(APIView):
    """
    LangGraph 기반 멀티 에이전트 API
    """
    
    def post(self, request, *args, **kwargs):
        """
        메시지 처리 API
        """
        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 세션 ID (인증된 사용자의 경우 사용자 ID 활용 가능)
        session_id = request.session.session_key or request.headers.get('X-Session-ID', 'default')
        
        # 세션 서비스 초기화
        session_manage_service = SessionManageService()
        conversation_history_service = ConversationHistoryService()
        
        # 세션 가져오기 또는 생성
        session = session_manage_service.get_or_create_session(session_id)

        # 에이전트 실행기 초기화
        agent_executor = ItineraryAgentExecutor()

        # LangGraph 서비스 초기화
        langgraph_service = LangGraphService(agent_executor)
        
        # 이전 대화 기록 가져오기 (Streamlit에서 전달한 경우)
        message_history = request.data.get('history', [])
        
        # 대화 기록이 있으면 세션에 메시지 복원
        for history_msg in message_history:
            if 'role' in history_msg and 'content' in history_msg:
                conversation_history_service.save_message(
                    session=session,
                    role=history_msg['role'],
                    content=history_msg['content']
                )

        # 멀티 에이전트 처리
        result = langgraph_service.process_message(
            session_id=session_id,
            message=serializer.validated_data['message']
        )
        
        return Response(result, status=status.HTTP_200_OK) 