from rest_framework import serializers
from tripmind.models.itinerary import Itinerary, SharedItinerary
from django.contrib.auth.models import User


class ItineraryRequestSerializer(serializers.Serializer):
    """여행 일정 생성 요청 시리얼라이저"""

    destination = serializers.CharField(required=True)
    duration = serializers.CharField(required=True)
    travelers = serializers.CharField(required=False, allow_blank=True)
    budget = serializers.CharField(required=False, allow_blank=True)
    preferences = serializers.CharField(required=False, allow_blank=True)
    special_requirements = serializers.CharField(required=False, allow_blank=True)


class ItineraryResponseSerializer(serializers.Serializer):
    """여행 일정 응답 시리얼라이저"""

    itinerary_plan = serializers.CharField()
    destination = serializers.CharField()
    duration = serializers.CharField()
    # 다른 필드들 추가


class ItineraryModelSerializer(serializers.ModelSerializer):
    """여행 일정 모델 시리얼라이저"""

    share_url = serializers.SerializerMethodField()
    expires_in_days = serializers.SerializerMethodField()
    is_share_valid = serializers.SerializerMethodField()

    class Meta:
        model = Itinerary
        fields = "__all__"

    def get_share_url(self, obj):
        request = self.context.get("request")
        if request and obj.is_public and obj.is_share_valid():
            return request.build_absolute_uri(
                f"/api/tripmind/share/itinerary/{obj.share_id}/"
            )
        return None

    def get_expires_in_days(self, obj):
        """공유 링크 만료까지 남은 일수"""
        if obj.share_expires_at:
            from django.utils import timezone
            from datetime import timedelta

            now = timezone.now()
            if obj.share_expires_at > now:
                delta = obj.share_expires_at - now
                return delta.days
        return None

    def get_is_share_valid(self, obj):
        """공유 링크 유효 여부"""
        return obj.is_share_valid()


class PublicItinerarySerializer(serializers.ModelSerializer):
    """공개 공유용 여행 일정 시리얼라이저 (민감 정보 제외)"""

    class Meta:
        model = Itinerary
        fields = ["title", "destination", "duration", "itinerary_plan", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    """사용자 시리얼라이저"""

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class ShareItineraryRequestSerializer(serializers.Serializer):
    """일정 공유 요청 시리얼라이저"""

    email = serializers.EmailField(required=True)
    can_edit = serializers.BooleanField(default=False)


class SharedItinerarySerializer(serializers.ModelSerializer):
    """공유된 일정 시리얼라이저"""

    itinerary = ItineraryModelSerializer(read_only=True)
    shared_with = UserSerializer(read_only=True)

    class Meta:
        model = SharedItinerary
        fields = ["id", "itinerary", "shared_with", "can_edit", "created_at"]


class PublicShareSettingSerializer(serializers.Serializer):
    is_public = serializers.BooleanField(required=True)
    share_type = serializers.ChoiceField(
        choices=Itinerary.SHARE_TYPE_CHOICES, default="VIEW"
    )
    expires_in_days = serializers.IntegerField(
        required=False, default=7, min_value=1, max_value=30
    )


class ExternalShareSerializer(serializers.Serializer):
    share_url = serializers.URLField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)
    share_type = serializers.CharField(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)


class MessageSerializer(serializers.Serializer):
    """메시지 요청 시리얼라이저"""

    message = serializers.CharField(required=True)
    history = serializers.ListField(required=False, child=serializers.DictField())
