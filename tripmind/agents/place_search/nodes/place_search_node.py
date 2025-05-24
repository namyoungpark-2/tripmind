from typing import Dict, Any
import os
import logging
from tripmind.agents.place_search.utils.query_builder import build_search_query
from tripmind.services.place_search.kakao_place_search_service import (
    KakaoPlaceSearchService,
)
from tripmind.clients.place_search.kakao_place_client import KakaoPlaceClient
from ..types.place_search_state_type import (
    PlaceSearchState,
    PlaceSearchContext,
    LastSearch,
)
from ..utils.formatting import format_places_results

logger = logging.getLogger(__name__)

kakao_place_search_service = KakaoPlaceSearchService(
    KakaoPlaceClient(os.getenv("KAKAO_REST_KEY"))
)


def place_search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """장소 검색 노드"""
    try:
        # 상태 객체 생성
        search_state = PlaceSearchState(
            messages=state.get("messages", []),
            parsed_info=state.get("parsed_info", {}),
            context=PlaceSearchContext(),
            next_node="conversation",
        )

        # 검색 쿼리 구성
        query = build_search_query(search_state.get("parsed_info", {}))
        location = search_state.get("parsed_info", {}).get("location")
        count = search_state.get("parsed_info", {}).get("count")
        # 장소 검색 실행
        print(f"count: {count}")
        search_results = kakao_place_search_service.search_places(
            query=query, location=location, size=int(count)
        )

        # 응답 메시지 생성
        if search_results:
            response_text = f"'{query}' 검색 결과입니다:\n\n"
            response_text += format_places_results(search_results)

            if location:
                response_text += (
                    f"\n\n참고: 지역 '{location}'에 대한 필터링이 적용되었습니다."
                )

            response_text += (
                "\n\n더 자세한 정보나 다른 장소를 알고 싶으시면 말씀해주세요."
            )
        else:
            response_text = f"죄송합니다. '{query}'에 대한 검색 결과가 없습니다. 다른 조건으로 시도해보시겠어요?"

        # 상태 업데이트
        search_state["messages"].append({"role": "assistant", "content": response_text})
        search_state["context"]["last_search"] = LastSearch(
            query=query, location=location, results=search_results
        )

        return dict(search_state)

    except Exception as e:
        logger.error(f"장소 검색 오류: {str(e)}")
        error_message = f"장소 검색 중 오류가 발생했습니다: {str(e)}"

        search_state["messages"].append({"role": "assistant", "content": error_message})
        return PlaceSearchState(
            messages=state.get("messages", [])
            + [{"role": "assistant", "content": error_message}],
            parsed_info=state.get("parsed_info", {}),
            context=PlaceSearchContext(last_search=None),
            next_node="conversation",
        )
