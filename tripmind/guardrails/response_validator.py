import re
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class ResponseValidator:
    @staticmethod
    def validate_urls(text: str) -> Tuple[str, List[str]]:
        issues = []
        url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
        urls = re.findall(url_pattern, text)

        allowed_domains = [
            "tripmind.com",
            "localhost",
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
                modified_text = modified_text.replace(url, "[확인되지 않은 링크]")

        return modified_text, issues

    @staticmethod
    def validate_price_info(text: str) -> Tuple[str, List[str]]:
        issues = []

        price_patterns = [
            r"(\d{1,3}(?:,\d{3})+)원",
            r"(\d+)만원",
            r"(\d+)원",
            r"₩(\d{1,3}(?:,\d{3})*)",
            r"\$(\d{1,3}(?:,\d{3})*)",
        ]

        modified_text = text

        for pattern in price_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                price_str = match.group(0)
                if (
                    "약" not in price_str
                    and "대략" not in price_str
                    and "보통" not in price_str
                ):
                    replacement = f"약 {price_str}"
                    modified_text = modified_text.replace(price_str, replacement)
                    issues.append(
                        f"정확한 가격 정보를 근사 표현으로 변경: {price_str} → {replacement}"
                    )

        return modified_text, issues

    @staticmethod
    def validate_time_info(text: str) -> Tuple[str, List[str]]:
        issues = []

        operation_time_patterns = [
            r"영업시간[은는이가]?\s*(\d{1,2}:\d{2})\s*~\s*(\d{1,2}:\d{2})",
            r"운영시간[은는이가]?\s*(\d{1,2}:\d{2})\s*~\s*(\d{1,2}:\d{2})",
            r"개장시간[은는이가]?\s*(\d{1,2}:\d{2})\s*~\s*(\d{1,2}:\d{2})",
            r"(\d{1,2}:\d{2})\s*~\s*(\d{1,2}:\d{2})\s*까지\s*영업",
            r"(\d{1,2}:\d{2})\s*부터\s*(\d{1,2}:\d{2})\s*까지",
        ]

        modified_text = text

        certainty_words = ["보통", "일반적으로", "대개", "대부분", "약", "주로"]

        for pattern in operation_time_patterns:
            matches = re.finditer(pattern, modified_text)
            for match in matches:
                time_str = match.group(0)

                has_certainty_word = False
                for word in certainty_words:
                    if word in time_str or re.search(
                        r"{}[\s]?{}".format(word, time_str), modified_text
                    ):
                        has_certainty_word = True
                        break

                if not has_certainty_word:
                    replacement = f"일반적으로 {time_str}"
                    modified_text = modified_text.replace(time_str, replacement)
                    issues.append(
                        f"정확한 운영시간 표현을 완화: {time_str} → {replacement}"
                    )

        return modified_text, issues

    @staticmethod
    def remove_fabricated_contacts(text: str) -> Tuple[str, List[str]]:

        issues = []

        phone_patterns = [
            r"(?<!\d)010-\d{4}-\d{4}(?!\d)",
            r"(?<!\d)02-\d{3,4}-\d{4}(?!\d)",
            r"(?<!\d)0\d{1,2}-\d{3,4}-\d{4}(?!\d)",
            r"(?<!\d)\+82[ -]?\d{1,2}[ -]?\d{3,4}[ -]?\d{4}(?!\d)",
        ]

        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        modified_text = text

        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            for phone in phones:
                modified_text = modified_text.replace(phone, "[연락처 확인 필요]")
                issues.append(f"임의 생성된 전화번호 제거: {phone}")

        emails = re.findall(email_pattern, text)
        for email in emails:
            if not any(
                domain in email
                for domain in ["tripmind.com", "kakao.com", "google.com"]
            ):
                modified_text = modified_text.replace(email, "[이메일 확인 필요]")
                issues.append(f"임의 생성된 이메일 제거: {email}")

        return modified_text, issues

    @staticmethod
    def check_hallucinations(text: str) -> List[str]:
        issues = []

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

        all_issues = []
        modified_text = text

        modified_text, issues = ResponseValidator.validate_urls(modified_text)
        all_issues.extend(issues)

        modified_text, issues = ResponseValidator.validate_price_info(modified_text)
        all_issues.extend(issues)

        modified_text, issues = ResponseValidator.validate_time_info(modified_text)
        all_issues.extend(issues)

        modified_text, issues = ResponseValidator.remove_fabricated_contacts(
            modified_text
        )
        all_issues.extend(issues)

        hallucination_issues = ResponseValidator.check_hallucinations(modified_text)
        all_issues.extend(hallucination_issues)

        if all_issues:
            logger.warning(f"응답 검증 결과 {len(all_issues)}개 문제 발견:")
            for i, issue in enumerate(all_issues):
                logger.warning(f"  {i+1}. {issue}")
        else:
            logger.info("응답 검증 완료: 문제 없음")

        return modified_text
