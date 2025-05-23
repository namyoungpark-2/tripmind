from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tripmind.agents.conversation.conversation_agent_executor import (
    ConversationAgentExecutor,
)
from tripmind.agents.itinerary.itinerary_agent_executor import (
    ItineraryAgentExecutor,
)
from tripmind.agents.prompt_router.constants.intent_constants import Intent
from tripmind.agents.prompt_router.prompt_router_agent_executor import (
    PromptRouterAgentExecutor,
)
from tripmind.api.serializers.itinerary_serializer import MessageSerializer
from tripmind.services.itinerary.itinerary_service import LangGraphService
from tripmind.services.session.session_manage_service import session_manage_service


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
        session_id = request.session.session_key or request.headers.get(
            "X-Session-ID", "default"
        )

        # 세션 가져오기 또는 생성
        session = session_manage_service.get_or_create_session(session_id)
        prompt = serializer.validated_data["message"]
        prompt_router_agent_excutor = PromptRouterAgentExecutor()
        router_result = prompt_router_agent_excutor.process_prompt(
            prompt=prompt,
            session_id=session_id,
        )
        intent = router_result["intent"]
        next_node = router_result["next_node"]

        print(f"메시지: '{prompt}' -> 분류된 의도: {intent}")

        # 에이전트 실행기 초기화
        # MCP (MULTI CHAT PROCESS) 에이전트 실행기로 확장 가능
        # 현재는 여행 일정 전문 에이전트 실행기로 사용

        if intent == Intent.ITINERARY.value:
            print("여행 일정 전문 에이전트 실행")
            agent_executor = ItineraryAgentExecutor()
        else:
            print("일반 대화 에이전트 실행")
            agent_executor = ConversationAgentExecutor()

        # LangGraph 서비스 초기화
        langgraph_service = LangGraphService(agent_executor)

        # 이전 대화 기록 가져오기 (Streamlit에서 전달한 경우)
        # message_history = request.data.get("history", [])

        # # 대화 기록이 있으면 세션에 메시지 복원
        # for history_msg in message_history:
        #     if "role" in history_msg and "content" in history_msg:
        #         conversation_history_service.save_message(
        #             session=session,
        #             role=history_msg["role"],
        #             content=history_msg["content"],
        #         )

        # 멀티 에이전트 처리
        result = langgraph_service.process_message(
            session_id=session_id,
            message=serializer.validated_data["message"],
            start_node=next_node,
        )

        # conversation_history_service.save_conversation(
        #     session_id,
        #     serializer.validated_data["message"],
        #     result.get("response", "응답을 생성하지 못했습니다."),
        # )

        return Response(result, status=status.HTTP_200_OK)
