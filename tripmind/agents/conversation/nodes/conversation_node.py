from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableMap
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any
import logging

from tripmind.services.session.session_manage_service import session_manage_service

logger = logging.getLogger(__name__)


def conversation_node(llm: ChatAnthropic, state: Dict[str, Any]) -> Dict[str, Any]:
    """검색 노드"""
    try:
        # 세션 ID 가져오기 (스레드 ID를 세션 ID로 사용)
        config = state.get("config_data", {})
        session_id = config.get("thread_id", "default")

        user_input = state["user_input"]
        base_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "당신은 여행 일정 전문 AI 에이전트입니다."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        memory = session_manage_service.get_session_memory(session_id)
        chat_history = memory.load_memory_variables({}).get("chat_history", [])

        lang_chain = (
            RunnableMap(
                {
                    "input": lambda x: x["input"],
                    "chat_history": lambda x: x.get("chat_history", []),
                    "agent_scratchpad": lambda x: x.get("agent_scratchpad", []),
                    "model": lambda x: x.get("model", llm.model),
                }
            )
            | base_prompt
            | llm
            | StrOutputParser()
        )

        # LLM 호출
        response = lang_chain.invoke(
            {
                "input": user_input,
                "chat_history": chat_history,
                "agent_scratchpad": [],
                "model": llm.model,
            }
        )

        memory.save_context({"input": user_input}, {"output": response})

        # 메시지 추가
        if "messages" not in state:
            state["messages"] = []

        state["messages"].append({"role": "assistant", "content": response})

        # 응답과 함께 전체 상태 반환
        return {**state, "response": response}

    except Exception as e:
        logger.error(f"General error: {str(e)}")
        logger.exception("Full stack trace:")
        error_message = f"[대화 생성 오류] {str(e)}"

        # 오류 메시지를 포함한 상태 반환
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({"role": "assistant", "content": error_message})
        return {**state, "response": error_message}
