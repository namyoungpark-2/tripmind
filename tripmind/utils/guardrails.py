import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class ResponseValidator:
    """LLM 응답 검증 및 표준화 클래스"""

    @staticmethod
    def validate_urls(text: str) -> Tuple[str, List[str]]:
        """
        텍스트에서 URL을 추출하고 유효성 검사

        Args:
            text: 검사할 텍스트

        Returns:
            수정된 텍스트, 발견된 문제점 목록
        """
        issues = []

        # URL 패턴
        url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"

        # 텍스트에서 URL 찾기
        urls = re.findall(url_pattern, text)

        # 허용된 도메인 목록 (예시)
        allowed_domains = [
            "tripmind.com",
            "localhost",
            "example.com",  # 개발용
            "kakao.com",
            "google.com",
            "maps.google.com",
        ]

        modified_text = text

        for url in urls:
            is_allowed = False
            for domain in allowed_domains:
                if domain in url:
                    is_allowed = True
                    break

            if not is_allowed:
                issues.append(f"허용되지 않은 URL 발견: {url}")
                # URL 제거 또는 마스킹 (여기서는 [확인되지 않은 링크]로 대체)
                modified_text = modified_text.replace(url, "[확인되지 않은 링크]")

        return modified_text, issues

    @staticmethod
    def validate_price_info(text: str) -> Tuple[str, List[str]]:
        """
        가격 정보의 유효성 검사

        Args:
            text: 검사할 텍스트

        Returns:
            수정된 텍스트, 발견된 문제점 목록
        """
        issues = []

        # 가격 형식 패턴들
        price_patterns = [
            r"(\d{1,3}(?:,\d{3})+)원",  # 100,000원
            r"(\d+)만원",  # 10만원
            r"(\d+)원",  # 1000원
            r"₩(\d{1,3}(?:,\d{3})*)",  # ₩10,000
            r"\$(\d{1,3}(?:,\d{3})*)",  # $100
        ]

        modified_text = text

        # 모든 가격 패턴에 대해 검사
        for pattern in price_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                price_str = match.group(0)
                if (
                    "약" not in price_str
                    and "대략" not in price_str
                    and "보통" not in price_str
                ):
                    # 정확한 가격 정보는 추측일 가능성이 높으므로 근사 표현으로 변경
                    replacement = f"약 {price_str}"
                    modified_text = modified_text.replace(price_str, replacement)
                    issues.append(
                        f"정확한 가격 정보를 근사 표현으로 변경: {price_str} → {replacement}"
                    )

        return modified_text, issues

    @staticmethod
    def validate_time_info(text: str) -> Tuple[str, List[str]]:
        """
        영업시간, 운영시간 등 시간 정보 유효성 검사

        Args:
            text: 검사할 텍스트

        Returns:
            수정된 텍스트, 발견된 문제점 목록
        """
        issues = []

        # 영업시간 패턴
        operation_time_patterns = [
            r"영업시간[은는이가]?\s*(\d{1,2}:\d{2})\s*~\s*(\d{1,2}:\d{2})",
            r"운영시간[은는이가]?\s*(\d{1,2}:\d{2})\s*~\s*(\d{1,2}:\d{2})",
            r"개장시간[은는이가]?\s*(\d{1,2}:\d{2})\s*~\s*(\d{1,2}:\d{2})",
            r"(\d{1,2}:\d{2})\s*~\s*(\d{1,2}:\d{2})\s*까지\s*영업",
            r"(\d{1,2}:\d{2})\s*부터\s*(\d{1,2}:\d{2})\s*까지",
        ]

        modified_text = text

        # 확실한 표현을 나타내는 단어들
        certainty_words = ["보통", "일반적으로", "대개", "대부분", "약", "주로"]

        for pattern in operation_time_patterns:
            matches = re.finditer(pattern, modified_text)
            for match in matches:
                time_str = match.group(0)

                # 이미 확률적 표현이 있는지 확인
                has_certainty_word = False
                for word in certainty_words:
                    if word in time_str or re.search(
                        r"{}[\s]?{}".format(word, time_str), modified_text
                    ):
                        has_certainty_word = True
                        break

                if not has_certainty_word:
                    # 정확한 시간은 변경될 수 있으므로 '일반적으로'를 추가
                    replacement = f"일반적으로 {time_str}"
                    modified_text = modified_text.replace(time_str, replacement)
                    issues.append(
                        f"정확한 운영시간 표현을 완화: {time_str} → {replacement}"
                    )

        return modified_text, issues

    @staticmethod
    def remove_fabricated_contacts(text: str) -> Tuple[str, List[str]]:
        """
        임의 생성된 연락처 정보 제거

        Args:
            text: 검사할 텍스트

        Returns:
            수정된 텍스트, 발견된 문제점 목록
        """
        issues = []

        # 전화번호 패턴
        phone_patterns = [
            r"(?<!\d)010-\d{4}-\d{4}(?!\d)",  # 010-1234-5678
            r"(?<!\d)02-\d{3,4}-\d{4}(?!\d)",  # 02-123-4567 or 02-1234-5678
            r"(?<!\d)0\d{1,2}-\d{3,4}-\d{4}(?!\d)",  # 지역번호
            r"(?<!\d)\+82[ -]?\d{1,2}[ -]?\d{3,4}[ -]?\d{4}(?!\d)",  # 국제 번호
        ]

        # 이메일 패턴
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        modified_text = text

        # 전화번호 검사 및 제거
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            for phone in phones:
                modified_text = modified_text.replace(phone, "[연락처 확인 필요]")
                issues.append(f"임의 생성된 전화번호 제거: {phone}")

        # 이메일 검사 및 제거
        emails = re.findall(email_pattern, text)
        for email in emails:
            # 일부 공식 이메일은 허용
            if not any(
                domain in email
                for domain in ["tripmind.com", "example.com", "kakao.com", "google.com"]
            ):
                modified_text = modified_text.replace(email, "[이메일 확인 필요]")
                issues.append(f"임의 생성된 이메일 제거: {email}")

        return modified_text, issues

    @staticmethod
    def check_hallucinations(text: str, known_entities: List[str] = None) -> List[str]:
        """
        가능한 환각 내용 탐지 (확정적 주장 탐지)

        Args:
            text: 검사할 텍스트
            known_entities: 알려진 실제 엔티티 목록 (장소, 식당명 등)

        Returns:
            발견된 문제점 목록
        """
        issues = []

        # 확정적 주장을 나타내는 표현들
        definitive_patterns = [
            r"반드시",
            r"무조건",
            r"항상",
            r"절대",
            r"확실히",
            r"틀림없이",
            r"확정적으로",
            r"예외 없이",
            r"오직",
            r"유일하게",
        ]

        # 확정적 표현 검사
        for pattern in definitive_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                context_start = max(0, match.start() - 20)
                context_end = min(len(text), match.end() + 20)
                context = text[context_start:context_end]
                issues.append(
                    f"확정적 주장 발견: '{context}' 부분에서 '{pattern}' 표현 사용"
                )

        return issues

    @staticmethod
    def validate_response(text: str) -> str:
        """
        종합적인 응답 검증 및 표준화

        Args:
            text: 검사할 텍스트

        Returns:
            검증되고 수정된 텍스트
        """
        all_issues = []
        modified_text = text

        # URL 검증
        modified_text, issues = ResponseValidator.validate_urls(modified_text)
        all_issues.extend(issues)

        # 가격 정보 검증
        modified_text, issues = ResponseValidator.validate_price_info(modified_text)
        all_issues.extend(issues)

        # 시간 정보 검증
        modified_text, issues = ResponseValidator.validate_time_info(modified_text)
        all_issues.extend(issues)

        # 연락처 정보 제거
        modified_text, issues = ResponseValidator.remove_fabricated_contacts(
            modified_text
        )
        all_issues.extend(issues)

        # 환각 내용 탐지
        hallucination_issues = ResponseValidator.check_hallucinations(modified_text)
        all_issues.extend(hallucination_issues)

        # 발견된 모든 문제를 로깅
        if all_issues:
            logger.warning(f"응답 검증 결과 {len(all_issues)}개 문제 발견:")
            for i, issue in enumerate(all_issues):
                logger.warning(f"  {i+1}. {issue}")
        else:
            logger.info("응답 검증 완료: 문제 없음")

        return modified_text


class NodeValidator:
    """LangGraph 노드 검증 클래스"""

    @staticmethod
    def validate_state(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        상태 객체의 유효성 검증

        Args:
            state: 검증할 상태 객체

        Returns:
            검증된 상태 객체
        """
        # 필수 키 확인 및 초기화
        if not isinstance(state, dict):
            logger.error(f"상태 객체가 딕셔너리가 아님: {type(state)}")
            return {"messages": [], "error": "상태 객체 형식 오류"}

        # 필수 키 확인 및 초기화
        for key in ["messages", "user_input"]:
            if key not in state:
                logger.warning(f"상태 객체에 '{key}' 키 없음, 초기화")
                if key == "messages":
                    state[key] = []
                else:
                    state[key] = ""

        # 메시지 형식 검증
        if "messages" in state and isinstance(state["messages"], list):
            validated_messages = []
            for msg in state["messages"]:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    # 메시지 내용 검증
                    if msg["role"] == "assistant" and isinstance(msg["content"], str):
                        # AI 응답 내용 검증
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
        """
        특정 노드의 응답 검증

        Args:
            node_name: 노드 이름
            response: 검증할 응답

        Returns:
            검증된 응답
        """
        logger.info(f"'{node_name}' 노드 응답 검증 시작: {len(response)} 글자")

        # 기본 응답 검증
        validated = ResponseValidator.validate_response(response)

        # 노드별 추가 검증
        if node_name == "sharing_node":
            # 공유 노드 특화 검증 (링크 포함 여부 등)
            if "공유 링크" in validated and "http" not in validated:
                logger.warning("공유 노드 응답에 링크 없음")
                validated += (
                    "\n\n(공유 링크가 생성되지 않았습니다. 나중에 다시 시도해주세요.)"
                )

        elif node_name == "itinerary_node":
            # 일정 노드 특화 검증 (일정 포맷 등)
            if "일차" not in validated and "일정" in validated:
                logger.warning("일정 노드 응답에 일차별 계획 없음")
                validated += "\n\n(더 자세한 일정을 원하시면 추가 정보를 제공해주세요.)"

        elif node_name == "calendar_node":
            # 캘린더 노드 특화 검증
            if (
                "캘린더" in validated
                and "등록" in validated
                and "성공" not in validated
            ):
                logger.warning("캘린더 등록 성공 여부 불명확")
                validated += "\n\n(캘린더 등록 상태를 확인해주세요.)"

        logger.info(f"'{node_name}' 노드 응답 검증 완료")
        return validated


# 편의 함수들
def validate_llm_response(response: str) -> str:
    """응답 검증 간편 함수"""
    return ResponseValidator.validate_response(response)


def validate_node_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """노드 상태 검증 간편 함수"""
    return NodeValidator.validate_state(state)


def validate_node_response(node_name: str, response: str) -> str:
    """노드 응답 검증 간편 함수"""
    return NodeValidator.validate_response_for_node(node_name, response)
