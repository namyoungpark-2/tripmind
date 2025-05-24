import re
from tripmind.agents.place_search.types.place_info_type import PlaceInfo


def parse_place_info(prompt: str) -> PlaceInfo:
    info = PlaceInfo(
        location=None,
        category=None,
        subcategory=None,
        mood=None,
        price_range=None,
        count=None,
    )

    location_patterns = [
        r"서울|부산|인천|대구|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주",
        r"([가-힣]+구|시|군|읍|면|동)",
    ]

    for pattern in location_patterns:
        match = re.search(pattern, prompt)
        if match:
            info["location"] = match.group(0)
            break
        else:
            info["location"] = "서울"

    category_patterns = {
        "맛집": ["맛집", "식당", "음식점", "레스토랑"],
        "카페": ["카페", "커피숍", "디저트"],
        "관광지": ["관광지", "명소", "볼거리", "여행지"],
        "쇼핑": ["쇼핑", "마트", "시장", "상가"],
    }

    for category, patterns in category_patterns.items():
        if any(pattern in prompt for pattern in patterns):
            info["category"] = category
            break

    if info["category"] == "맛집":
        subcategory_patterns = {
            "한식": ["한식", "한국음식", "한국料理"],
            "일식": ["일식", "일본음식", "일본料理", "초밥", "스시"],
            "중식": ["중식", "중국음식", "중국料理"],
            "양식": ["양식", "서양음식", "이탈리안", "프렌치"],
            "카페": ["카페", "디저트", "브런치"],
        }

        for subcategory, patterns in subcategory_patterns.items():
            if any(pattern in prompt for pattern in patterns):
                info["subcategory"] = subcategory
                break

    mood_patterns = {
        "로맨틱": ["로맨틱", "데이트", "커플"],
        "가족": ["가족", "아이", "어린이"],
        "친구": ["친구", "단체", "모임"],
        "비즈니스": ["비즈니스", "회의", "미팅"],
    }

    for mood, patterns in mood_patterns.items():
        if any(pattern in prompt for pattern in patterns):
            info["mood"] = mood
            break

    price_patterns = {
        "저가": ["저렴", "싼", "저가", "가성비"],
        "중가": ["보통", "적당", "중가"],
        "고가": ["고급", "비싼", "고가", "럭셔리"],
    }

    for price, patterns in price_patterns.items():
        if any(pattern in prompt for pattern in patterns):
            info["price_range"] = price
            break

    count_patterns = {
        "1": ["1개", "1개만", "1개만 추천"],
        "2": ["2개", "2개만", "2개만 추천"],
        "3": ["3개", "3개만", "3개만 추천"],
        "4": ["4개", "4개만", "4개만 추천"],
        "5": ["5개", "5개만", "5개만 추천"],
        "6": ["6개", "6개만", "6개만 추천"],
        "7": ["7개", "7개만", "7개만 추천"],
        "8": ["8개", "8개만", "8개만 추천"],
        "9": ["9개", "9개만", "9개만 추천"],
        "10": ["10개", "10개만", "10개만 추천"],
    }

    for count, patterns in count_patterns.items():
        if any(pattern in prompt for pattern in patterns):
            info["count"] = count
            break
        else:
            info["count"] = 5
    return info
