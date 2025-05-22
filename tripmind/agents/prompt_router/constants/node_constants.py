from enum import Enum


class NodeType(str, Enum):
    INPUT = "input"
    ROUTER = "router"
    ITINERARY = "itinerary"
    GREETING = "greeting"
    ASK_INFO = "ask_info"
    PLACE_SEARCH = "place_search"
    CALENDAR = "calendar"
    CONVERSATION = "conversation"
    SHARING = "sharing"
    END = "end"


# 노드별 설명
NODE_DESCRIPTIONS = {
    NodeType.INPUT: "사용자 입력 처리",
    NodeType.ROUTER: "의도에 따른 라우팅",
    NodeType.ITINERARY: "여행 일정 생성",
}
