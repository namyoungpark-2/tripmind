from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def validate_share_request(share_info: Dict[str, Any]) -> Dict[str, Any]:
    validated = {**share_info}

    if validated.get("share_type") not in ["VIEW", "EDIT"]:
        logger.warning(
            f"잘못된 공유 유형: {validated.get('share_type')}, 기본값 VIEW로 설정"
        )
        validated["share_type"] = "VIEW"

    try:
        days = int(validated.get("days", 7))
        if days < 1:
            logger.warning(f"공유 기간이 너무 짧음: {days}일, 최소 1일로 설정")
            days = 1
        elif days > 30:
            logger.warning(f"공유 기간이 너무 김: {days}일, 최대 30일로 제한")
            days = 30
        validated["days"] = days
    except (ValueError, TypeError):
        logger.warning(
            f"잘못된 공유 기간 형식: {validated.get('days')}, 기본값 7일로 설정"
        )
        validated["days"] = 7

    if validated.get("share_method") not in ["URL", "KAKAO", "EMAIL", "SMS"]:
        logger.warning(f"잘못된 공유 방식: {validated.get('share_method')}, URL로 설정")
        validated["share_method"] = "URL"

    return validated
