from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tripmind.agents.tools.place_search_tool import PlaceSearchTool
from tripmind.llm.prompt_loader import prompt_loader
from tripmind.agents.types.itinerary_state_type import ItineraryState
from tripmind.services.external.kakao_place_search_service import kakao_place_search_service
from tripmind.services.session_manage_service import session_manage_service
from typing import Dict, Any

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.callbacks.base import BaseCallbackHandler

import logging

logger = logging.getLogger(__name__)


# 커스텀 콜백 핸들러 생성
class ToolUsageCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.tool_usage = []
        self.logger = logging.getLogger("tool_usage")
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        tool_name = serialized.get("name", "unknown_tool")
        self.logger.info(f"도구 시작: {tool_name}, 입력: {input_str}")
        self.tool_usage.append({
            "tool": tool_name,
            "input": input_str,
            "output": None,
            "status": "started"
        })
    
    def on_tool_end(self, output, **kwargs):
        if self.tool_usage:
            self.tool_usage[-1]["output"] = output
            self.tool_usage[-1]["status"] = "completed"
            self.logger.info(f"도구 완료: 출력: {output}")
    
    def on_tool_error(self, error, **kwargs):
        if self.tool_usage:
            self.tool_usage[-1]["error"] = str(error)
            self.tool_usage[-1]["status"] = "error"
            self.logger.error(f"도구 오류: {error}")
    
    def get_tool_usage(self):
        return self.tool_usage


def itinerary_node(llm: ChatAnthropic, state: ItineraryState) -> ItineraryState:
    """일정 생성 노드"""
    try:
        # 입력 데이터 구성
        user_input = state.get("user_input", "")
        context = state.get("context", {})
        messages = state.get("messages", [])

        # 세션 ID 가져오기 (스레드 ID를 세션 ID로 사용)
        config = state.get("config_data", {})
        session_id = config.get("thread_id", "default")

        # 프롬프트 구성
        full_prompt = ""

        # 이전 대화 기록이 있으면 포함 (요약본만 포함)
        if len(messages) > 1:  # 현재 사용자 메시지를 제외한 이전 대화가 있는 경우
            # 최근 3개의 대화만 포함
            recent_messages = messages[:-1][-3:]
            if recent_messages:
                full_prompt += "이전 대화 요약:\n"
                for msg in recent_messages:
                    role = "사용자" if msg["role"] == "user" else "AI"
                    # 내용이 너무 길면 자르기
                    content = msg["content"]
                    if len(content) > 200:
                        content = content[:197] + "..."
                    full_prompt += f"{role}: {content}\n\n"
            
        full_prompt += "현재 요청:\n"

        # 현재 요청 추가
        full_prompt += user_input

        if context:
                additional_info = ""
                for key, value in context.items():
                    if value:
                        additional_info += f"\n- {key}: {value}"
                
                if additional_info:
                    full_prompt += f"\n\n추가 정보:{additional_info}"
        
        agent_executor, tool_usage_callback = get_itinerary_node_agent(llm, session_id)
        # response = agent_executor.invoke({"input": full_prompt})

        # 중간 단계 추적 옵션 추가
        result = agent_executor.invoke(
            {"input": full_prompt},
            {"return_intermediate_steps": True}
        )
        
        # 도구 사용 정보 확인
        tool_usage = tool_usage_callback.get_tool_usage()
        logger.info(f"도구 사용 내역: {tool_usage}")
        
        # 도구 사용 결과를 상태에 저장
        state["tool_usage"] = tool_usage
        
        # 결과가 딕셔너리면 'output' 필드 확인
        # 중간 단계 추적 옵션 추가
        if isinstance(result, dict) and "output" in result:
            output = result["output"]
            
            # output이 JSON 문자열 형태(도구 호출 액션)인지 확인
            if isinstance(output, str) and output.startswith('{"action":'):
                logger.info("도구 호출 응답을 감지했습니다. 최종 응답 생성 중...")
                
                # 기존 대화 기록과 도구 호출 결과를 포함하여 최종 응답 생성 요청
                last_tool_result = None
                if "intermediate_steps" in result and result["intermediate_steps"]:
                    last_action, last_output = result["intermediate_steps"][-1]
                    last_tool_result = f"도구 이름: {last_action.tool}\n도구 입력: {last_action.tool_input}\n도구 결과: {last_output}"
                
                # 최종 응답 생성 요청
                final_prompt = f"""이전에 도구 호출을 수행했습니다. 이제 사용자의 질문에 대한 최종 답변을 생성해주세요.
                원래 사용자 요청: {full_prompt}
                {last_tool_result if last_tool_result else ''}
                """

                # 최종 응답 생성
                final_response = llm.invoke(final_prompt).content
                
                # 응답 저장
                state["messages"].append({"role": "assistant", "content": final_response})
                return {**state, "response": final_response}
            else:
                # 일반 응답인 경우
                response = output
        else:
            # 결과가 딕셔너리가 아니면 문자열로 변환
            response = str(result)
        
        final_response = response
        
        if "tool_usage" in state and state["tool_usage"]:
            tool_usage_text = "\n\n[도구 사용 내역]\n"
            for i, usage in enumerate(state["tool_usage"], 1):
                tool_usage_text += f"{i}. {usage['tool']} 도구 사용\n"
                tool_usage_text += f"   입력: {usage['input']}\n"
                if len(str(usage['output'])) > 100:
                    tool_usage_text += f"   출력: {str(usage['output'])[:100]}...\n"
                else:
                    tool_usage_text += f"   출력: {usage['output']}\n"
            print(f"도구 사용 내역: {tool_usage_text}")

        # 응답 저장
        state["messages"].append({"role": "assistant", "content": final_response})
        return {**state, "response": final_response}
        
    except Exception as e:
        logger.error(f"General error: {str(e)}")
        logger.exception("Full stack trace:")
        error_response = f"[여행 일정 생성 오류] {str(e)}"
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({"role": "assistant", "content": error_response})
        return {**state, "response": error_response}

def get_itinerary_node_agent(llm: ChatAnthropic, session_id: str) -> Dict[str, Any]:
    place_search_tool = PlaceSearchTool(kakao_place_search_service)

    memory = session_manage_service.get_session_memory(session_id)

    tools = place_search_tool.get_langchain_tools()
    tool_descriptions = [
        f"Tool: {tool.name}\nDescription: {tool.description}\n" 
        for tool in tools
    ]
    formatted_tools = "\n".join(tool_descriptions)
    tool_names = [tool.name for tool in tools]

    system_prompt = prompt_loader.load_prompt_template_from_yaml("itinerary/v1.yaml")
    system_prompt += "\n\n중요: 도구를 사용한 후에는 반드시 최종 응답을 생성해야 합니다. 도구 결과만 반환하지 마세요. 도구 결과를 바탕으로 사용자의 질문에 답변해주세요."

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = (
        {
            "input": lambda x: x["input"],
            "chat_history": lambda x: x.get("chat_history", []),
            "agent_scratchpad": lambda x: format_to_openai_function_messages(x.get("intermediate_steps", [])),
            "tools": lambda x: formatted_tools,
            "tool_names": lambda x: ", ".join(tool_names)
        } 
        | prompt 
        | llm 
        | OpenAIFunctionsAgentOutputParser()
    )

    # 도구 사용 추적 콜백 추가
    tool_usage_callback = ToolUsageCallbackHandler()

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
        max_execution_time=None,
        early_stopping_method="force",
        return_intermediate_steps=True  # 중간 단계 결과 반환 추가
    )
        
    return agent_executor, tool_usage_callback