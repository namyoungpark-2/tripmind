from typing import Dict, Any
import logging
from pathlib import Path
from tripmind.clients.llm.base_llm_client import BaseLLMClient
from tripmind.services.prompt.prompt_service import prompt_service
from langchain.chains import LLMChain

logger = logging.getLogger(__name__)

PROMPT_DIR = Path(__file__).parent / "../prompt_templates"


def conversation_node(
    llm_client: BaseLLMClient, state: Dict[str, Any]
) -> Dict[str, Any]:
    try:
        session_id = state.get("config_data", {}).get("thread_id", "default")
        config = {"configurable": {"session_id": session_id}}

        user_input = state["user_input"]
        prompt = prompt_service.get_system_prompt(
            str(PROMPT_DIR / "conversation/v1.yaml"),
        )

        prompt = prompt.partial(
            model=llm_client.get_llm().model,
        )

        chain = LLMChain(
            llm=llm_client.get_llm(),
            prompt=prompt,
            verbose=True,
            output_key="output",
        )

        response = chain.invoke(
            {
                "input": user_input,
                "chat_history": state.get("messages", []),
                "agent_scratchpad": [],
                "model": llm_client.get_llm().model,
            },
            config=config,
        )

        print("response", response)
        try:
            if isinstance(response, dict):
                response_text = response["output"]
            else:
                response_text = str(response)
        except Exception as e:
            logger.error(f"의도 파싱 중 오류: {str(e)}")

        state["messages"].append({"role": "assistant", "content": response_text})
        return {**state, "response": response_text}

    except Exception as e:
        logger.error(f"General error: {str(e)}")
        logger.exception("Full stack trace:")
        error_message = f"[대화 생성 오류] {str(e)}"

        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({"role": "assistant", "content": error_message})
        return {**state, "response": error_message}
