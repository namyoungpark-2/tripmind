from langchain.tools import StructuredTool
from tripmind.agents.itinerary.types.final_response_tool_type import FinalResponseInput


def final_response_tool_fn(response: str) -> str:
    return response


# 3. StructuredTool 정의
FinalResponseTool = StructuredTool.from_function(
    name="FinalResponse",
    description="사용자에게 최종 응답을 전달하는 툴입니다. response 필드에 최종 출력 메시지를 넣으세요.",
    func=final_response_tool_fn,
    args_schema=FinalResponseInput,
    return_direct=True,  # 이걸 설정해야 사용자에게 바로 출력됨
)
