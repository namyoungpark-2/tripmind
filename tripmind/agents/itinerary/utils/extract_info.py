from typing import Dict
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
