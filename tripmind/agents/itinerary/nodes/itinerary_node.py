import os
import re
import time
from tripmind.agents.itinerary.tools.calendar_tool import get_calendar_tools
from tripmind.agents.itinerary.tools.place_search_tool import get_place_search_tools
from tripmind.agents.itinerary.utils.extract_info import extract_travel_info
from tripmind.clients.calendar.google_calendar_client import GoogleCalendarClient
from tripmind.clients.llm.base_llm_client import BaseLLMClient
from tripmind.services.calendar.google_calendar_service import GoogleCalendarService
from tripmind.services.prompt.prompt_service import prompt_service
from tripmind.agents.itinerary.types.itinerary_state_type import ItineraryState
from tripmind.services.place_search.kakao_place_search_service import (
    KakaoPlaceSearchService,
)
from tripmind.clients.place_search.kakao_place_client import KakaoPlaceClient
from typing import Dict, Any
from pathlib import Path
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_structured_chat_agent
import logging
from anthropic import APIStatusError

logger = logging.getLogger(__name__)
PROMPT_DIR = Path(__file__).parent / "../prompt_templates"

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def itinerary_node(llm_client: BaseLLMClient, state: ItineraryState) -> ItineraryState:
    """일정 생성 노드"""
    try:
        user_input = state.get("user_input", "")
        context = state.get("context", {})
        session_id = state.get("config_data", {}).get("thread_id", "default")
        previous_results = state.get("previous_results", {})
        state["previous_results"] = previous_results
        travel_info = extract_travel_info(user_input)
        for key, value in travel_info.items():
            if value:
                context[key] = value

        full_prompt = _get_full_prompt(state)

        agent_executor = get_itinerary_node_agent(llm_client, state)

        # 도구 설명과 이름 가져오기
        tool_descriptions = [
            f"Tool: {tool.name}\nDescription: {tool.description}\n"
            for tool in agent_executor.tools
        ]
        formatted_tools = "\n".join(tool_descriptions)
        tool_names = [tool.name for tool in agent_executor.tools]

        config = {
            "configurable": {"session_id": session_id},
        }

        for attempt in range(MAX_RETRIES):
            try:
                result = agent_executor.invoke(
                    {
                        "input": full_prompt,
                        "chat_history": state.get("messages", []),
                        "tools": formatted_tools,
                        "tool_names": ", ".join(tool_names),
                        "agent_scratchpad": [],
                    },
                    config=config,
                )
                break
            except APIStatusError as e:
                if "overloaded_error" in str(e) and attempt < MAX_RETRIES - 1:
                    logger.warning(
                        f"API 과부하 오류 발생. {RETRY_DELAY}초 후 재시도... (시도 {attempt + 1}/{MAX_RETRIES})"
                    )
                    time.sleep(RETRY_DELAY)
                    continue
                raise

        # 도구 실행 결과 추적
        intermediate_steps = result.get("intermediate_steps", [])
        print("[DEBUG] intermediate_steps:", intermediate_steps)

        executed_tool_inputs = set()
        tool_executions = []

        for action, output in intermediate_steps:
            key = (action.tool, str(action.tool_input))
            if key in executed_tool_inputs:
                final_response = "동일한 도구를 반복해서 사용하여 일정을 종료합니다."
                state["messages"].append(
                    {"role": "assistant", "content": final_response}
                )
                return {**state, "response": final_response}
            executed_tool_inputs.add(key)
            tool_executions.append(
                {"tool": action.tool, "input": action.tool_input, "output": output}
            )
            print(f"[DEBUG] 도구 실행 결과: {action.tool} - {output}")

        state["tool_executions"] = tool_executions

        if "tool_usage" in state and state["tool_usage"]:
            tool_usage_text = "\n\n[도구 사용 내역]\n"
            for i, usage in enumerate(state["tool_usage"], 1):
                tool_usage_text += f"{i}. {usage['tool']} 도구 사용\n"
                tool_usage_text += f"   입력: {usage['input']}\n"
                if len(str(usage["output"])) > 100:
                    tool_usage_text += f"   출력: {str(usage['output'])[:100]}...\n"
                else:
                    tool_usage_text += f"   출력: {usage['output']}\n"
            print(f"도구 사용 내역: {tool_usage_text}")

        # 최종 응답 결정
        output = result.get("output", "")
        if isinstance(output, str):
            if "Action: FinalAnswer" in output:
                # 최종 답변이면 Action Input 추출
                match = re.search(r"Action Input:\s*(.+)", output, re.DOTALL)
                if match:
                    final_answer = match.group(1).strip()
                    state["messages"].append(
                        {"role": "assistant", "content": final_answer}
                    )
                    return {**state, "response": final_answer}
            else:
                # 일반 텍스트 응답
                state["messages"].append({"role": "assistant", "content": output})
                return {**state, "response": output}
        else:
            state["messages"].append({"role": "assistant", "content": str(output)})
            return {**state, "response": str(output)}

    except Exception as e:
        logger.error(f"General error: {str(e)}")
        logger.exception("Full stack trace:")
        error_response = f"[여행 일정 생성 오류] {str(e)}"
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({"role": "assistant", "content": error_response})
        return {**state, "response": error_response}


def get_itinerary_node_agent(
    llm_client: BaseLLMClient, state: ItineraryState
) -> Dict[str, Any]:
    kakao_place_search_service = KakaoPlaceSearchService(
        KakaoPlaceClient(
            os.getenv("KAKAO_REST_KEY", "7582a0567cfa228ec8c38f2e3dafe03a")
        )
    )
    place_search_tools = get_place_search_tools(kakao_place_search_service)

    google_calendar_service = GoogleCalendarService(
        GoogleCalendarClient(
            os.getenv("GOOGLE_CALENDAR_ID"),
            os.getenv("GOOGLE_CREDENTIALS_PATH"),
        )
    )
    calendar_tools = get_calendar_tools(google_calendar_service)

    tools = place_search_tools + calendar_tools
    tool_descriptions = [
        f"Tool: {tool.name}\nDescription: {tool.description}\n" for tool in tools
    ]
    formatted_tools = "\n".join(tool_descriptions)
    tool_names = [tool.name for tool in tools]

    system_prompt = prompt_service.get_system_prompt(
        str(PROMPT_DIR / "itinerary/v1.yaml"),
    )
    system_prompt = system_prompt.partial(
        tools=formatted_tools,
        tool_names=", ".join(tool_names),
    )
    agent = create_structured_chat_agent(
        llm=llm_client.get_llm(), tools=tools, prompt=system_prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="input",
            output_key="output",
        ),
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=15,
        max_execution_time=None,
        early_stopping_method="force",
    )

    return agent_executor


def _get_full_prompt(state: ItineraryState) -> str:
    user_input = state.get("user_input", "")
    context = state.get("context", {})
    messages = state.get("messages", [])

    full_prompt = ""

    if not messages:
        messages.append({"role": "system", "content": "여행 일정을 도와드릴게요."})
    messages.append({"role": "user", "content": user_input})

    if len(messages) > 1:
        recent_messages = messages[:-1][-3:]
        if recent_messages:
            full_prompt += "이전 대화 요약:\n"
            for msg in recent_messages:
                role = "사용자" if msg["role"] == "user" else "AI"
                content = msg["content"]
                if len(content) > 200:
                    content = content[:197] + "..."
                full_prompt += f"{role}: {content}\n\n"

    if context:
        additional_info = ""
        for key, value in context.items():
            if value:
                additional_info += f"\n- {key}: {value}"

        if additional_info:
            full_prompt += f"\n\n추가 정보:{additional_info}"

    full_prompt += "현재 요청:\n"

    full_prompt += user_input

    return full_prompt
