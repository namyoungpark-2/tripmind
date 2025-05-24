from typing import List, Pattern
from dataclasses import dataclass
from pydantic import BaseModel, Field


class IntentResponse(BaseModel):
    intent: str = Field(description="분류된 의도")


@dataclass
class IntentPatterns:
    patterns: List[Pattern]
    keywords: List[str] = None

    def matches(self, text: str) -> bool:
        # 키워드 매칭
        if self.keywords and any(kw in text for kw in self.keywords):
            return True

        # 패턴 매칭
        return any(pattern.search(text) for pattern in self.patterns)
