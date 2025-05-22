from django.urls import path
from tripmind.api.views.conversation_history_view import ConversationHistoryAPIView
from tripmind.api.views.langgraph_api_view import LangGraphAPIView
from tripmind.api.views.itinerary_api_view import (
    ItineraryDetailAPIView,
    ItineraryShareAPIView,
    ItineraryShareRemoveAPIView,
    ItineraryPublicShareAPIView,
    PublicItineraryViewAPIView,
)

app_name = "tripmind"

urlpatterns = [
    path(
        "conversation/",
        ConversationHistoryAPIView.as_view(),
        name="conversation-history",
    ),
    path("langgraph/", LangGraphAPIView.as_view(), name="langgraph"),
    # 여행 일정 API
    path(
        "itinerary/<int:itinerary_id>/",
        ItineraryDetailAPIView.as_view(),
        name="itinerary-detail",
    ),
    # 여행 일정 공유 API
    path(
        "itinerary/<int:itinerary_id>/share/",
        ItineraryShareAPIView.as_view(),
        name="itinerary-share",
    ),
    path(
        "itinerary/<int:itinerary_id>/share/<int:share_id>/",
        ItineraryShareRemoveAPIView.as_view(),
        name="itinerary-share-remove",
    ),
    path(
        "itinerary/<int:itinerary_id>/public/",
        ItineraryPublicShareAPIView.as_view(),
        name="itinerary-public",
    ),
    # 공개 공유 링크
    path(
        "share/itinerary/<uuid:share_id>/",
        PublicItineraryViewAPIView.as_view(),
        name="public-itinerary",
    ),
]
