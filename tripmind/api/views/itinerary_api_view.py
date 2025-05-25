import json
from django.http import StreamingHttpResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from tripmind.agents.sharing.sharing_agent_executor import SharingRouterAgentExecutor
from tripmind.agents.calendar.calendar_agent_executor import CalendarRouterAgentExecutor
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


# 프로덕션 환경에서는 비활성화 해야함
@method_decorator(csrf_exempt, name="dispatch")
class ItineraryAPIView(View):
    """
    여행 일정 전문 에이전트 API
    """

    def post(self, request, *args, **kwargs):
        """
        메시지 처리 API
        """
        try:
            data = json.loads(request.body)
            serializer = MessageSerializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            session_id = request.session.session_key or request.headers.get(
                "X-Session-ID", "default"
            )

            prompt = serializer.validated_data["message"]
            agent_executor = self._get_agent_executor(Intent.CLASSIFY_INTENT.value)

            router_result = agent_executor.process_prompt(
                prompt=prompt,
                session_id=session_id,
            )

            intent = router_result["intent"]
            next_node = router_result["next_node"]

            print(f"메시지: '{prompt}' -> 분류된 의도: {intent}")

            agent_executor = self._get_agent_executor(intent)

            itinerary_service = ItineraryService(agent_executor)

            return StreamingHttpResponse(
                self._event_stream(
                    itinerary_service, session_id, serializer, next_node
                ),
                content_type="text/event-stream",
            )
        except json.JSONDecodeError:
            return Response(
                {"error": "잘못된 JSON 형식입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_agent_executor(self, intent):
        if intent == Intent.CLASSIFY_INTENT.value:
            return PromptRouterAgentExecutor()
        elif intent == Intent.ITINERARY.value:
            return ItineraryAgentExecutor()
        elif intent == Intent.PLACE_SEARCH.value:
            return PlaceSearchAgentExecutor()
        elif intent == Intent.SHARING.value:
            return SharingRouterAgentExecutor()
        elif intent == Intent.CALENDAR.value:
            return CalendarRouterAgentExecutor()
        else:
            return ConversationAgentExecutor()

    def _event_stream(self, itinerary_service, session_id, serializer, next_node):
        try:
            for result in itinerary_service.process_message(
                session_id=session_id,
                message=serializer.validated_data["message"],
                start_node=next_node,
            ):
                if result:
                    yield f"data: {json.dumps(result)}\n\n"
        except Exception as e:
            error_response = {
                "error": str(e),
                "response": f"[대화 오류] {str(e)}",
                "messages": [],
                "context": {},
            }
            yield f"data: {json.dumps(error_response)}\n\n"


class ItineraryDetailAPIView(View):
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


class ItineraryShareAPIView(View):
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


class ItineraryShareRemoveAPIView(View):
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
    def post(self, request, itinerary_id, *args, **kwargs):
        user = User.objects.get(id=1)
        itinerary = get_object_or_404(Itinerary, id=itinerary_id, user=user)
        serializer = PublicShareSettingSerializer(data=request.data)

        if serializer.is_valid():
            is_public = serializer.validated_data["is_public"]
            share_type = serializer.validated_data["share_type"]
            expires_in_days = serializer.validated_data.get("expires_in_days", 7)

            if not is_public:
                itinerary.is_public = False
                itinerary.share_type = "NONE"
                itinerary.share_expires_at = None
                itinerary.save()
                return Response({"message": "공유가 중지되었습니다."})

            share_url = itinerary.create_share_link(
                days=expires_in_days, share_type=share_type
            )

            response_data = {
                "share_url": share_url,
                "expires_at": itinerary.share_expires_at,
                "share_type": itinerary.share_type,
                "is_valid": True,
            }
            response_serializer = ExternalShareSerializer(instance=response_data)
            return Response(response_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublicItineraryViewAPIView(View):
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
