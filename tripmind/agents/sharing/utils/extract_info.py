from typing import Dict, Optional, Any
import re
import logging

logger = logging.getLogger(__name__)


def extract_travel_info(text: str) -> Dict[str, str]:
    info = {
        "destination": "",
        "duration": "",
        "travelers": "",
        "budget": "",
    }

    destination_pattern = r"([가-힣a-zA-Z]+)[\s]?(?:지역)"
    destination_match = re.search(destination_pattern, text)
    if destination_match:
        info["destination"] = destination_match.group(1)

    duration_patterns = [
        r"(\d+)[박]?\s?(\d+)?[일]?",
        r"(\d+)[\s]?일[\s]?동안",
        r"(\d+)[\s]?박[\s]?(\d+)[\s]?일",
    ]

    for pattern in duration_patterns:
        duration_match = re.search(pattern, text)
        if duration_match:
            info["duration"] = duration_match.group(0)
            break

    travelers_match = re.search(r"(\d+)[\s]?명", text)
    if travelers_match:
        info["travelers"] = travelers_match.group(0)

    budget_match = re.search(r"(\d+)[\s]?만원|(\d+)[\s]?원", text)
    if budget_match:
        info["budget"] = budget_match.group(0)

    return info


def extract_share_request(text: str) -> Optional[Dict[str, Any]]:
    share_patterns = [
        r"일정[\s]*(?:공유|공개)[\s]*(해줘|해 줘|할래|하자|부탁해|부탁|좀)",
        r"(?:공유|공개)[\s]*(?:링크|URL)[\s]*(?:만들어|생성|줘|좀)",
        r"(?:친구|가족|같이|동료)[\s]*(?:에게|한테|와|과|랑)[\s]*(?:공유|보여|전달)",
        r"url[\s]*(?:생성|만들어|보내)",
        r"공유[\s]*(?:하고 싶어|하고싶어|하고 싶|하고싶|좀)",
        r"링크[\s]*(?:만들어|생성|보내|줘|주세요)",
        r"(?:카톡|카카오톡|메일|이메일|문자)[\s]*(?:으로|로)[\s]*(?:공유|보내|전송|전달)",
        r"(?:카톡|카카오톡|메일|이메일|문자)[\s]*보내",
        r"일정[\s]*(?:내보내|외부|밖으로|보내)",
    ]

    is_share_request = False
    matched_pattern = None

    for pattern in share_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            is_share_request = True
            matched_pattern = match.group(0)
            break

    if not is_share_request:
        return None

    logger.info(f"공유 요청 감지: '{matched_pattern}' 패턴으로 인식")

    share_type = "VIEW"
    if re.search(
        r"(?:수정|편집|변경|업데이트)[\s]*(?:가능|할 수|허용|권한)", text, re.IGNORECASE
    ):
        share_type = "EDIT"
        logger.info("편집 가능한 공유 요청 감지")

    days = 7
    duration_match = re.search(r"(\d+)[\s]*(?:일|날짜|기간|day)", text, re.IGNORECASE)
    if duration_match:
        days = int(duration_match.group(1))
        days = min(max(1, days), 30)
        logger.info(f"공유 기간 설정: {days}일")

    share_method = None
    if re.search(r"(?:카톡|카카오톡)", text, re.IGNORECASE):
        share_method = "KAKAO"
    elif re.search(r"(?:메일|이메일|email)", text, re.IGNORECASE):
        share_method = "EMAIL"
    elif re.search(r"(?:문자|SMS|메시지)", text, re.IGNORECASE):
        share_method = "SMS"

    return {
        "share_type": share_type,
        "days": days,
        "share_method": share_method,
        "matched_pattern": matched_pattern,
    }
