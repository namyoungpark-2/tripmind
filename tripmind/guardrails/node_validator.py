import logging
from typing import Dict, Any
from tripmind.guardrails.response_validator import ResponseValidator

logger = logging.getLogger(__name__)


class NodeValidator:
    @staticmethod
    def validate_state(state: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(state, dict):
            logger.error(f"상태 객체가 딕셔너리가 아님: {type(state)}")
            return {"messages": [], "error": "상태 객체 형식 오류"}

        for key in ["messages", "user_input"]:
            if key not in state:
                logger.warning(f"상태 객체에 '{key}' 키 없음, 초기화")
                if key == "messages":
                    state[key] = []
                else:
                    state[key] = ""

        if "messages" in state and isinstance(state["messages"], list):
            validated_messages = []
            for msg in state["messages"]:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    if msg["role"] == "assistant" and isinstance(msg["content"], str):
                        msg["content"] = ResponseValidator.validate_response(
                            msg["content"]
                        )
                    validated_messages.append(msg)
                else:
                    logger.warning(f"잘못된 메시지 형식 무시: {msg}")
            state["messages"] = validated_messages

        return state

    @staticmethod
    def validate_response_for_node(node_name: str, response: str) -> str:
        logger.info(f"'{node_name}' 노드 응답 검증 시작: {len(response)} 글자")

        validated = ResponseValidator.validate_response(response)

        if node_name == "sharing_node":
            # 공유 노드 특화 검증 (링크 포함 여부 등)
            if "공유 링크" in validated and "http" not in validated:
                logger.warning("공유 노드 응답에 링크 없음")
                validated += (
                    "\n\n(공유 링크가 생성되지 않았습니다. 나중에 다시 시도해주세요.)"
                )

        elif node_name == "itinerary_node":
            if "일차" not in validated and "일정" in validated:
                logger.warning("일정 노드 응답에 일차별 계획 없음")
                validated += "\n\n(더 자세한 일정을 원하시면 추가 정보를 제공해주세요.)"

        elif node_name == "calendar_node":
            if (
                "캘린더" in validated
                and "등록" in validated
                and "성공" not in validated
            ):
                logger.warning("캘린더 등록 성공 여부 불명확")
                validated += "\n\n(캘린더 등록 상태를 확인해주세요.)"

        logger.info(f"'{node_name}' 노드 응답 검증 완료")
        return validated
