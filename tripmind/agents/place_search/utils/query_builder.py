from typing import Dict, Optional


def build_search_query(parsed_info: Dict[str, Optional[str]]) -> str:
    """검색 쿼리 구성"""
    query_parts = []

    for key in ["category", "subcategory", "mood", "price_range"]:
        if value := parsed_info.get(key):
            query_parts.append(value)

    return " ".join(query_parts) if query_parts else "맛집"
