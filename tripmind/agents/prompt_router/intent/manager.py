import re
from typing import Dict

from tripmind.agents.prompt_router.constants.intent_constants import (
    Intent,
)
from tripmind.agents.prompt_router.types.indent_type import IntentPatterns


class IntentPatternManager:
    def __init__(self):
        self._patterns: Dict[str, IntentPatterns] = {
            "greeting": IntentPatterns(
                patterns=[
                    re.compile(r"안녕|인녕하세요|반가워|반갑습니다|안녕하세요"),
                ]
            ),
            "calendar": IntentPatterns(
                patterns=[
                    re.compile(r"일정[을를]?\s*(?:추가|등록|확인|보여|조회)"),
                    re.compile(r"캘린더"),
                    re.compile(r"스케줄"),
                    re.compile(r"약속"),
                    re.compile(r"미팅"),
                    re.compile(r"(?:오늘|내일|모레|이번주|이번\s*달)[의]?\s*일정"),
                ]
            ),
            "place_search": IntentPatterns(
                patterns=[
                    re.compile(r"(.+)(?:어디|위치|찾아|검색)"),
                    re.compile(r"(.+)(?:이|가) 어디"),
                    re.compile(r"(.+) 알려"),
                    re.compile(r"근처.+찾아"),
                    re.compile(r"(.+) 장소"),
                ],
                keywords=[
                    "위치",
                    "찾아줘",
                    "검색해줘",
                    "어디",
                    "알려줘",
                    "근처",
                    "주변",
                ],
            ),
            "sharing": IntentPatterns(
                patterns=[
                    re.compile(r"일정[\s]*(?:공유|공개)"),
                    re.compile(r"(?:공유|공개)[\s]*(?:링크|URL)"),
                    re.compile(
                        r"(?:친구|가족|같이|동료)[\s]*(?:에게|한테|와|과|랑)[\s]*(?:공유|보여|전달)"
                    ),
                    re.compile(r"url[\s]*(?:생성|만들어|보내)"),
                    re.compile(r"공유[\s]*(?:하고 싶어|하고싶어|좀)"),
                ]
            ),
            "itinerary": IntentPatterns(
                patterns=[],
                keywords=[
                    "일정",
                    "계획",
                    "스케줄",
                    "짜줘",
                    "만들어",
                    "여행",
                    "itinerary",
                    "travel",
                ],
            ),
            "end": IntentPatterns(patterns=[], keywords=["종료", "끝", "그만"]),
        }

    def determine_intent_by_rule_based(self, text: str) -> str:
        text = text.lower()

        if self._patterns["end"].matches(text):
            return Intent.END.value

        # 캘린더 의도 확인
        if self._patterns["calendar"].matches(text):
            return Intent.ITINERARY.value

        # 장소 검색 의도 확인
        if self._patterns["place_search"].matches(text):
            return Intent.PLACE_SEARCH.value

        # 일정 공유 의도 확인
        if self._patterns["sharing"].matches(text):
            return Intent.SHARING.value

        # 일정 생성 의도 확인
        if self._patterns["itinerary"].matches(text):
            return Intent.ITINERARY.value

        # 인사 의도 확인
        if self._patterns["greeting"].matches(text):
            return Intent.GREETING.value

        return Intent.UNKNOWN.value


intent_pattern_manager = IntentPatternManager()
