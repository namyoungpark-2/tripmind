from enum import Enum


class Intent(str, Enum):
    ITINERARY = "itinerary"
    CONVERSATION = "conversation"
    GREETING = "greeting"
    UNKNOWN = "unknown"


# 의도별 설명
INTENT_DESCRIPTIONS = {
    Intent.ITINERARY: "여행 일정 짜기",
    Intent.CONVERSATION: "일반적인 대화",
    Intent.GREETING: "인사",
    Intent.UNKNOWN: "알 수 없음",
}

# 의도별 키워드
INTENT_KEYWORDS = {
    Intent.ITINERARY: ["일정", "계획", "스케줄", "짜줘", "만들어", "여행"],
    Intent.CONVERSATION: ["대화", "대화해줘", "대화해줘요", "대화해줘요"],
    Intent.GREETING: ["안녕", "인녕하세요", "반가워", "반갑습니다", "안녕하세요"],
    Intent.UNKNOWN: [
        "알 수 없음",
        "알 수 없음",
        "알 수 없음",
        "알 수 없음",
        "알 수 없음",
    ],
}

# 의도와 노드 매핑
INTENT_TO_NODE_MAP = {
    Intent.ITINERARY: "itinerary",
    Intent.CONVERSATION: "conversation",
    Intent.UNKNOWN: "conversation",
}
