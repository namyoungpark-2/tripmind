import os
import logging
import time

from tripmind.agents.place_search.utils.query_builder import build_search_query
from tripmind.services.place_search.kakao_place_search_service import (
    KakaoPlaceSearchService,
)
from tripmind.services.session.session_manage_service import session_manage_service
from tripmind.clients.place_search.kakao_place_client import KakaoPlaceClient
from ..types.place_search_state_type import (
    PlaceSearchState,
    PlaceSearchContext,
    LastSearch,
)
from ..utils.formatting import format_places_results

logger = logging.getLogger(__name__)


def place_search_node(state: PlaceSearchState) -> PlaceSearchState:
    try:
        user_input = state.get("user_input", "")
        query = build_search_query(state.get("parsed_info", {}))
        parsed_info = state.get("parsed_info", {})
        session_id = state.get("config_data", {}).get("thread_id", "default")
        messages = state.get("messages", [])

        location, count = (
            parsed_info.get("location"),
            parsed_info.get("count"),
        )

        kakao_place_search_service = KakaoPlaceSearchService(
            KakaoPlaceClient(os.getenv("KAKAO_REST_KEY"))
        )
        search_results = kakao_place_search_service.search_places(
            query=query, location=location, size=int(count or 5)
        )
        if search_results:
            response_text = f"'{query}' 검색 결과입니다:\n\n"
            response_text += format_places_results(search_results)
            response_text += (
                "\n\n더 자세한 정보나 다른 장소를 알고 싶으시면 말씀해주세요."
            )
        else:
            response_text = f"죄송합니다. '{query}'에 대한 검색 결과가 없습니다. 다른 조건으로 시도해보시겠어요?"

        place_search_context = PlaceSearchContext(
            last_search=LastSearch(
                query=query,
                location=location,
                results=[result.model_dump() for result in search_results],
            )
        )

        current_message = response_text[:0]
        message = messages + [{"role": "assistant", "content": current_message}]

        memory = session_manage_service.get_session_memory(
            session_id,
            memory_key="chat_history",
            input_key="input",
            output_key="output",
        )
        memory.save_context(
            inputs={memory.input_key: user_input},
            outputs={memory.output_key: response_text},
        )

        return PlaceSearchState(
            messages=message,
            parsed_info=parsed_info,
            context=place_search_context,
            next_node="update_place_search_stream",
            streaming={
                "message": response_text,
                "current_position": 0,
                "is_complete": False,
            },
        )

    except Exception as e:
        logger.error(f"장소 검색 오류: {str(e)}")
        raise RuntimeError(f"[PlaceSearchNode] 오류 발생: {str(e)}")


def update_place_search_stream(state: PlaceSearchState) -> PlaceSearchState:
    try:
        streaming = state.get("streaming", {})
        messages = state.get("messages", [])

        if streaming["is_complete"]:
            return state

        chunk_size = 20
        current_pos = streaming["current_position"]
        next_pos = min(current_pos + chunk_size, len(streaming["message"]))

        streaming["current_position"] = next_pos

        streaming["is_complete"] = next_pos >= len(streaming["message"])
        current_message = streaming["message"][:next_pos]

        messages[-1]["content"] = current_message

        state["messages"] = messages
        state["next_node"] = "update_place_search_stream"
        time.sleep(1)  # 1초 대기
        return PlaceSearchState(**state)
    except Exception as e:
        return state
