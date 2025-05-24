from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from tripmind.agents.common.types.agent_executor_type import AgentExecutorResult
from tripmind.agents.place_search.place_search_agent_executor import (
    PlaceSearchAgentExecutor,
)
from tripmind.api.serializers.itinerary_serializer import (
    ItineraryModelSerializer,
    MessageSerializer,
    ShareItineraryRequestSerializer,
    SharedItinerarySerializer,
    PublicShareSettingSerializer,
    PublicItinerarySerializer,
    ExternalShareSerializer,
)
from tripmind.models.itinerary import Itinerary, SharedItinerary
from tripmind.services.itinerary.itinerary_service import ItineraryService
from tripmind.agents.itinerary.itinerary_agent_executor import ItineraryAgentExecutor
from tripmind.agents.conversation.conversation_agent_executor import (
    ConversationAgentExecutor,
)
from tripmind.agents.prompt_router.prompt_router_agent_executor import (
    PromptRouterAgentExecutor,
)
from tripmind.agents.prompt_router.constants.intent_constants import Intent


class ItineraryAPIView(APIView):
    """
    여행 일정 전문 에이전트 API
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
        prompt = serializer.validated_data["message"]
        prompt_router_agent_executor = PromptRouterAgentExecutor()

        router_result: AgentExecutorResult = (
            prompt_router_agent_executor.process_prompt(
                prompt=prompt,
                session_id=session_id,
            )
        )
        print("router_result", router_result)
        intent = router_result["intent"]
        next_node = router_result["next_node"]

        print(f"메시지: '{prompt}' -> 분류된 의도: {intent}")

        if intent == Intent.ITINERARY.value:
            print("여행 일정 전문 에이전트 실행")
            agent_executor = ItineraryAgentExecutor()
        elif intent == Intent.PLACE_SEARCH.value:
            print("장소 검색에이전트 실행")
            agent_executor = PlaceSearchAgentExecutor()
        else:
            print("일반 대화 에이전트 실행")
            agent_executor = ConversationAgentExecutor()

        itinerary_service = ItineraryService(agent_executor)

        # 멀티 에이전트 처리
        result = itinerary_service.process_message(
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


class ItineraryDetailAPIView(APIView):
    """여행 일정 상세 조회/수정/삭제 API"""

    permission_classes = [IsAuthenticated]

    def get(self, request, itinerary_id, *args, **kwargs):
        """일정 상세 조회"""
        itinerary = get_object_or_404(Itinerary, id=itinerary_id, user=request.user)
        serializer = ItineraryModelSerializer(itinerary, context={"request": request})
        return Response(serializer.data)

    def put(self, request, itinerary_id, *args, **kwargs):
        """일정 수정"""
        itinerary = get_object_or_404(Itinerary, id=itinerary_id, user=request.user)
        serializer = ItineraryModelSerializer(
            itinerary, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, itinerary_id, *args, **kwargs):
        """일정 삭제"""
        itinerary = get_object_or_404(Itinerary, id=itinerary_id, user=request.user)
        itinerary.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ItineraryShareAPIView(APIView):
    """여행 일정 공유 API"""

    permission_classes = [IsAuthenticated]

    def post(self, request, itinerary_id, *args, **kwargs):
        """일정 특정 사용자와 공유"""
        itinerary = get_object_or_404(Itinerary, id=itinerary_id, user=request.user)
        serializer = ShareItineraryRequestSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            can_edit = serializer.validated_data["can_edit"]

            try:
                user_to_share = User.objects.get(email=email)

                # 이미 공유된 경우 권한만 업데이트
                shared_itinerary, created = SharedItinerary.objects.update_or_create(
                    itinerary=itinerary,
                    shared_with=user_to_share,
                    defaults={"can_edit": can_edit},
                )

                response_serializer = SharedItinerarySerializer(shared_itinerary)
                return Response(
                    response_serializer.data,
                    status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
                )

            except User.DoesNotExist:
                return Response(
                    {"error": "해당 이메일을 가진 사용자가 존재하지 않습니다."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, itinerary_id, *args, **kwargs):
        """일정 공유 목록 조회"""
        itinerary = get_object_or_404(Itinerary, id=itinerary_id, user=request.user)
        shared_itineraries = SharedItinerary.objects.filter(itinerary=itinerary)
        serializer = SharedItinerarySerializer(shared_itineraries, many=True)
        return Response(serializer.data)


class ItineraryShareRemoveAPIView(APIView):
    """여행 일정 공유 해제 API"""

    permission_classes = [IsAuthenticated]

    def delete(self, request, itinerary_id, share_id, *args, **kwargs):
        """특정 사용자와의 공유 해제"""
        itinerary = get_object_or_404(Itinerary, id=itinerary_id, user=request.user)
        shared_itinerary = get_object_or_404(
            SharedItinerary, id=share_id, itinerary=itinerary
        )
        shared_itinerary.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ItineraryPublicShareAPIView(APIView):
    """여행 일정 공개 공유 설정 API"""

    permission_classes = [IsAuthenticated]

    def post(self, request, itinerary_id, *args, **kwargs):
        """일정 공개 여부 설정"""
        itinerary = get_object_or_404(Itinerary, id=itinerary_id, user=request.user)
        serializer = PublicShareSettingSerializer(data=request.data)

        if serializer.is_valid():
            # 공유 설정 업데이트
            is_public = serializer.validated_data["is_public"]
            share_type = serializer.validated_data["share_type"]
            expires_in_days = serializer.validated_data.get("expires_in_days", 7)

            # 공유 중지 설정
            if not is_public:
                itinerary.is_public = False
                itinerary.share_type = "NONE"
                itinerary.share_expires_at = None
                itinerary.save()
                return Response({"message": "공유가 중지되었습니다."})

            # 공유 링크 생성
            share_url = itinerary.create_share_link(
                days=expires_in_days, share_type=share_type
            )

            # 응답 데이터 구성
            response_data = {
                "share_url": request.build_absolute_uri(
                    f"/api/tripmind/share/itinerary/{itinerary.share_id}/"
                ),
                "expires_at": itinerary.share_expires_at,
                "share_type": itinerary.share_type,
                "is_valid": True,
            }

            response_serializer = ExternalShareSerializer(data=response_data)
            if response_serializer.is_valid():
                return Response(response_serializer.data)
            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublicItineraryViewAPIView(APIView):
    """공개된 여행 일정 조회 API - 로그인 불필요"""

    def get(self, request, share_id, *args, **kwargs):
        """공유 링크로 일정 조회"""
        itinerary = get_object_or_404(Itinerary, share_id=share_id)

        # 공유 유효성 검사
        if not itinerary.is_public:
            return Response(
                {"error": "이 일정은 더 이상 공개되지 않습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if itinerary.share_expires_at and itinerary.share_expires_at < timezone.now():
            return Response(
                {"error": "공유 링크가 만료되었습니다."}, status=status.HTTP_410_GONE
            )

        # 권한에 따라 다른 시리얼라이저 사용
        if itinerary.share_type == "EDIT":
            # 편집 권한이 있는 경우, 더 많은 정보 제공
            serializer = ItineraryModelSerializer(
                itinerary, context={"request": request}
            )
        else:
            # 기본 조회 권한
            serializer = PublicItinerarySerializer(itinerary)

        return Response(serializer.data)
