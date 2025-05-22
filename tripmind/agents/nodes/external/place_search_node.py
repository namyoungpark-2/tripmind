from typing import Dict, Any, List, Optional
import re
import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from tripmind.agents.tools.place_search_tool import PlaceSearchTool

logger = logging.getLogger(__name__)

place_search_tool = PlaceSearchTool()


def extract_location_from_text(text: str) -> Optional[str]:
    """
    텍스트에서 위치 정보 추출 시도
    형식: "서울", "부산", "제주도" 등
    """
    location_pattern = r"(?:위치|지역|장소|근처):?\s*([가-힣a-zA-Z0-9\s]+)"
    location_match = re.search(location_pattern, text)

    if location_match:
        return location_match.group(1).strip()

    # 주요 도시 이름 패턴
    cities = [
        "서울",
        "부산",
        "인천",
        "대구",
        "대전",
        "광주",
        "울산",
        "세종",
        "제주",
        "수원",
        "고양",
        "용인",
        "성남",
        "부천",
        "화성",
        "남양주",
    ]

    for city in cities:
        if city in text:
            return city

    return None


def extract_keyword_from_text(text: str) -> str:
    """
    텍스트에서 검색 키워드 추출
    """
    # "찾아줘", "검색해줘", "알려줘" 등의 패턴 앞에 있는 내용 추출
    keyword_pattern = r"([가-힣a-zA-Z0-9\s]+)(?:을|를)?\s*(?:찾아|검색|알려)"
    keyword_match = re.search(keyword_pattern, text)

    if keyword_match:
        return keyword_match.group(1).strip()

    # "~이 어디 있어?" 패턴
    where_pattern = r"([가-힣a-zA-Z0-9\s]+)(?:이|가)\s*어디"
    where_match = re.search(where_pattern, text)

    if where_match:
        return where_match.group(1).strip()

    # 단순히 공백으로 분리하여 처음 몇 단어 추출 (마지막 수단)
    words = text.split()
    if words and len(words) >= 2:
        return " ".join(words[:3])  # 처음 3개 단어만 사용

    return text  # 그 외의 경우 전체 텍스트 반환


def format_places_results(places: List[Dict]) -> str:
    """
    검색 결과를 텍스트로 포맷팅
    """
    if not places:
        return "검색 결과가 없습니다."

    results = []
    for i, place in enumerate(places[:5], 1):  # 최대 5개 결과만 표시
        name = place.get("name", "이름 없음")
        category = place.get("category", "").split(" > ")[
            -1
        ]  # 가장 구체적인 카테고리만 표시
        address = place.get("address", "주소 없음")
        phone = place.get("phone", "전화번호 없음")

        result = f"{i}. **{name}** ({category})\n"
        result += f"   - 주소: {address}\n"
        if phone and phone != "전화번호 없음":
            result += f"   - 전화: {phone}\n"

        results.append(result)

    return "\n".join(results)


def place_search_node(llm: ChatAnthropic, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    장소 검색 노드 - PlaceSearchTool을 사용하여 장소 정보 검색
    """
    try:
        # 사용자 입력 가져오기
        user_input = state.get("user_input", "")
        messages = state.get("messages", [])
        context = state.get("context", {})

        # 검색 키워드와 위치 추출
        keyword = extract_keyword_from_text(user_input)
        location = extract_location_from_text(user_input)

        # 추출된 정보가 부족하면 LLM에 분석 요청
        if not keyword or len(keyword) < 2:
            prompt = ChatPromptTemplate.from_template(
                """사용자가 어떤 장소나 시설을 찾으려고 합니다. 다음 메시지에서 검색해야 할 키워드를 추출해주세요.
                규칙:
                1. 가능한 구체적인 키워드를 찾아주세요.
                2. 불필요한 단어는 제외해주세요.
                3. 결과는 키워드만 반환해주세요.
                
                사용자 메시지: {message}
                
                키워드:"""
            )

            # LLM 호출
            keyword_response = llm.invoke(prompt.format(message=user_input))
            keyword = keyword_response.content.strip()

        logger.info(f"검색 키워드: {keyword}, 위치: {location}")
        # PlaceSearchTool을 사용한 장소 검색
        if location:
            search_results = place_search_tool.search_places(
                query=keyword, location=location
            )
        else:
            search_results = place_search_tool.search_places(query=keyword)

        # 결과 포맷팅
        if search_results:
            response_text = f"'{keyword}' 검색 결과입니다:\n\n"
            # response_text += format_places_results(search_results)
            response_text += search_results
            # 추가 정보 제공
            if location:
                response_text += (
                    f"\n\n참고: 지역 '{location}'에 대한 필터링이 적용되었습니다."
                )

            response_text += (
                "\n\n더 자세한 정보나 다른 장소를 알고 싶으시면 말씀해주세요."
            )
        else:
            response_text = f"죄송합니다. '{keyword}'에 대한 검색 결과가 없습니다. 다른 키워드로 시도해보시겠어요?"

        # 상태 업데이트
        if "messages" not in state:
            state["messages"] = []

        state["messages"].append({"role": "assistant", "content": response_text})

        # 컨텍스트에 검색 정보 저장
        context["last_search_keyword"] = keyword
        if location:
            context["last_search_location"] = location

        # 검색 결과 저장 (최대 5개만)
        context["search_results"] = search_results[:5] if search_results else []

        return {**state, "context": context, "response": response_text}

    except Exception as e:
        logger.error(f"장소 검색 오류: {str(e)}")
        logger.exception("전체 오류:")

        error_message = f"장소 검색 중 오류가 발생했습니다: {str(e)}"

        if "messages" not in state:
            state["messages"] = []

        state["messages"].append({"role": "assistant", "content": error_message})

        return {**state, "response": error_message}
