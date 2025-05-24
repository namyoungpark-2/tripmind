import os
import time
from tripmind.agents.itinerary.tools.calendar_tool import get_calendar_tools
from tripmind.agents.itinerary.tools.place_search_tool import get_place_search_tools
from tripmind.clients.calendar.google_calendar_client import GoogleCalendarClient
from tripmind.clients.llm.base_llm_client import BaseLLMClient
from tripmind.services.calendar.google_calendar_service import GoogleCalendarService
from tripmind.services.prompt.prompt_service import prompt_service
from tripmind.agents.itinerary.types.itinerary_state_type import ItineraryState
from tripmind.services.place_search.kakao_place_search_service import (
    KakaoPlaceSearchService,
)
from tripmind.clients.place_search.kakao_place_client import KakaoPlaceClient
from typing import Dict, Any, List
from pathlib import Path
from langchain.agents import AgentExecutor, create_structured_chat_agent
import logging
from tripmind.services.session.session_manage_service import session_manage_service
from langchain.tools import StructuredTool
from tripmind.agents.itinerary.tools.final_response_tool import FinalResponseTool
from tripmind.services.sharing.sharing_service import sharing_service

logger = logging.getLogger(__name__)
PROMPT_DIR = Path(__file__).parent / "../prompt_templates"


def itinerary_node(llm_client: BaseLLMClient, state: ItineraryState) -> ItineraryState:
    try:
        session_id = state.get("config_data", {}).get("thread_id", "default")
        previous_results = state.get("previous_results", {})
        state["previous_results"] = previous_results

        memory = session_manage_service.get_session_memory(
            session_id,
            memory_key="chat_history",
            input_key="input",
            output_key="output",
        )

        full_prompt = _get_full_prompt(state)

        place_search_tools = get_place_search_tools(
            KakaoPlaceSearchService(KakaoPlaceClient(os.getenv("KAKAO_REST_KEY")))
        )
        calendar_tools = get_calendar_tools(
            GoogleCalendarService(
                GoogleCalendarClient(
                    os.getenv("GOOGLE_CALENDAR_ID"),
                    os.getenv("GOOGLE_CREDENTIALS_PATH"),
                )
            )
        )

        tools = place_search_tools + calendar_tools + [FinalResponseTool]

        tool_descriptions = "\n".join(
            [f"Tool: {tool.name}\nDescription: {tool.description}\n" for tool in tools]
        )
        tool_names = [tool.name for tool in tools]

        agent_executor = create_itinerary_node_agent(
            llm_client, state, tools, tool_descriptions, tool_names
        )

        config = {
            "configurable": {"session_id": session_id},
        }

        result = agent_executor.invoke(
            {
                "input": full_prompt,
                "chat_history": memory.load_memory_variables({}).get(
                    "chat_history", []
                ),
                "tools": tool_descriptions,
                "tool_names": ", ".join(tool_names),
            },
            config=config,
        )

        if isinstance(result, dict):
            response_text = result.get("output", "")
        else:
            response_text = str(result)

        response_text = sharing_service.get_share_request(
            state.get("user_input", ""),
            response_text,
            state.get("context", {}),
            state.get("config_data", {}).get("base_url", "localhost:8000"),
        )

        state["streaming"] = {
            "message": response_text,
            "current_position": 0,
            "is_complete": False,
        }

        intermediate_steps = result.get("intermediate_steps", [])

        memory.save_context(
            inputs={
                memory.input_key: full_prompt,
                "agent_scratchpad": intermediate_steps,
            },
            outputs={memory.output_key: response_text},
        )

        current_message = response_text[: state["streaming"]["current_position"]]
        state["messages"].append({"role": "assistant", "content": current_message})
        state["next_node"] = "update_itinerary_stream"
        return ItineraryState(**state)

    except Exception as e:
        logger.error(f"General error: {str(e)}")
        logger.exception("Full stack trace:")
        error_response = f"[여행 일정 생성 오류] {str(e)}"
        state["messages"].append({"role": "assistant", "content": error_response})
        raise e


def update_itinerary_stream(state: ItineraryState) -> ItineraryState:
    try:
        streaming = state["streaming"]
        if streaming["is_complete"]:
            return state

        chunk_size = 50
        current_pos = streaming["current_position"]
        next_pos = min(current_pos + chunk_size, len(streaming["message"]))
        streaming["current_position"] = next_pos
        streaming["is_complete"] = next_pos >= len(streaming["message"])
        current_message = streaming["message"][:next_pos]
        state["messages"][-1]["content"] = current_message
        state["next_node"] = "update_itinerary_stream"
        time.sleep(1)
        return state

    except Exception as e:
        return state


def create_itinerary_node_agent(
    llm_client: BaseLLMClient,
    state: ItineraryState,
    tools: List[StructuredTool],
    tool_descriptions: str,
    tool_names: List[str],
) -> Dict[str, Any]:
    session_id = state.get("config_data", {}).get("thread_id", "default")
    system_prompt = prompt_service.get_system_prompt(
        str(PROMPT_DIR / "itinerary/v1.yaml"),
    )
    system_prompt = system_prompt.partial(
        model=llm_client.get_llm().model,
        tools=tool_descriptions,
        tool_names=", ".join(tool_names),
    )

    agent = create_structured_chat_agent(
        llm=llm_client.get_llm(), tools=tools, prompt=system_prompt
    )
    memory = session_manage_service.get_session_memory(
        session_id, memory_key="chat_history", input_key="input", output_key="output"
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
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
