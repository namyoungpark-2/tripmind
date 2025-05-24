from enum import Enum


class Intent(str, Enum):
    CLASSIFY_INTENT = "classify_intent"
    ITINERARY = "itinerary"
    CONVERSATION = "conversation"
    GREETING = "greeting"
    PLACE_SEARCH = "place_search"
    SHARING = "sharing"
    CALENDAR = "calendar"
    END = "end"
    UNKNOWN = "unknown"


# 의도별 설명
INTENT_DESCRIPTIONS = {
    Intent.CLASSIFY_INTENT: "의도 분류",
    Intent.ITINERARY: "여행 일정 짜기",
    Intent.CONVERSATION: "일반적인 대화",
    Intent.GREETING: "인사",
    Intent.PLACE_SEARCH: "장소 검색",
    Intent.SHARING: "일정 공유",
    Intent.CALENDAR: "캘린더",
    Intent.END: "종료",
    Intent.UNKNOWN: "알 수 없음",
}

# 의도별 키워드
INTENT_KEYWORDS = {
    Intent.ITINERARY: ["일정", "계획", "스케줄", "짜줘", "만들어", "여행"],
    Intent.CONVERSATION: ["대화", "대화해줘", "대화해줘요", "대화해줘요"],
    Intent.GREETING: ["안녕", "인녕하세요", "반가워", "반갑습니다", "안녕하세요"],
    Intent.SHARING: ["일정", "계획", "스케줄", "짜줘", "만들어", "여행"],
    Intent.CALENDAR: ["캘린더", "캘린더 보여줘", "캘린더 보여줘요", "캘린더 보여줘요"],
    Intent.END: ["종료", "끝", "그만"],
    Intent.PLACE_SEARCH: [
        "장소",
        "장소 찾아줘",
        "장소 찾아줘요",
        "장소 찾아줘요",
        "찾다",
        "찾아줘",
        "검색",
        "추천",
        "추천해줘",
        "추천해줘요",
    ],
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
    Intent.ITINERARY: "ask_info_node",
    Intent.CONVERSATION: "conversation_node",
    Intent.PLACE_SEARCH: "ask_info_node",
    Intent.SHARING: "sharing_node",
    Intent.CALENDAR: "ask_info_node",
    Intent.END: "end",
    Intent.UNKNOWN: "classify_intent_node",
    Intent.GREETING: "greeting_node",
}
