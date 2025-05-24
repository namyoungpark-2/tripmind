import logging
import traceback
import json
from pathlib import Path

from tripmind.agents.prompt_router.constants.intent_constants import (
    INTENT_DESCRIPTIONS,
    INTENT_TO_NODE_MAP,
    Intent,
)
from tripmind.agents.prompt_router.types.prompt_router_state_type import (
    PromptRouterState,
)
from tripmind.clients.llm.base_llm_client import BaseLLMClient
from tripmind.services.prompt.prompt_service import prompt_service
from langchain.chains import LLMChain

logger = logging.getLogger(__name__)

PROMPT_DIR = Path(__file__).parent / "../prompt_templates"


def classify_intent_node(
    llm_client: BaseLLMClient, state: PromptRouterState
) -> PromptRouterState:
    try:
        session_id = state.get("config_data", {}).get("session_id", "default")
        config = {"configurable": {"session_id": session_id}}
        user_input = state.get("user_input", "")
        next_node = state.get("next_node", "")

        intent_descriptions = "\n".join(
            [
                f"- {intent.value}: {description}"
                for intent, description in INTENT_DESCRIPTIONS.items()
            ]
        )

        prompt = prompt_service.get_system_prompt(
            str(PROMPT_DIR / "classify_intent/v1.yaml"),
        )

        prompt = prompt.partial(
            intent_descriptions=intent_descriptions,
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
                "chat_history": [],
            },
            config=config,
        )

        try:
            if isinstance(response, dict):
                if "output" in response:
                    intent_str = json.loads(response["output"])["intent"]
                else:
                    intent_str = response["intent"]
            else:
                intent_str = json.loads(str(response))["intent"]
        except Exception as e:
            logger.error(f"의도 파싱 중 오류: {str(e)}")
            intent_str = "conversation"

        if intent_str in [e.value for e in Intent]:
            if intent_str in [Intent.CALENDAR, Intent.SHARING, Intent.ITINERARY]:
                intent = Intent.ITINERARY
            else:
                intent = Intent(intent_str)
        else:
            intent = Intent.CONVERSATION

        next_node = INTENT_TO_NODE_MAP.get(intent, "conversation")

        state: PromptRouterState = {
            "user_input": user_input,
            "intent": intent.value,
            "next_node": next_node,
            "messages": state.get("messages", []),
            "context": {"intent": intent.value},
            "response": response,
        }

        return state

    except Exception as e:
        traceback.print_exc()
        return {
            "user_input": user_input,
            "intent": Intent.CONVERSATION.value,
            "next_node": "conversation",
            "messages": state.get("messages", []),
            "context": {"intent": Intent.CONVERSATION.value},
            "response": f"의도 분류 중 오류가 발생했습니다: {str(e)}",
        }
