import logging
import time
from pathlib import Path
from tripmind.clients.llm.base_llm_client import BaseLLMClient
from tripmind.services.prompt.prompt_service import prompt_service
from langchain.chains import LLMChain
from tripmind.agents.conversation.types.conversation_state_type import ConversationState
from tripmind.services.session.session_manage_service import session_manage_service

logger = logging.getLogger(__name__)

PROMPT_DIR = Path(__file__).parent / "../prompt_templates"


def conversation_node(
    llm_client: BaseLLMClient, state: ConversationState
) -> ConversationState:
    try:

        session_id = state.get("config_data", {}).get("thread_id", "default")
        config = {"configurable": {"session_id": session_id}}
        user_input = state["user_input"]
        memory = session_manage_service.get_session_memory(
            session_id,
            memory_key="chat_history",
            input_key="input",
            output_key="output",
        )
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
                "chat_history": memory.load_memory_variables({}).get(
                    "chat_history", []
                ),
                "agent_scratchpad": [],
                "model": llm_client.get_llm().model,
            },
            config=config,
        )

        if isinstance(response, dict):
            response_text = response["output"]
        else:
            response_text = str(response)

        state["streaming"] = {
            "message": response_text,
            "current_position": 0,
            "is_complete": False,
        }

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

        current_message = response_text[: state["streaming"]["current_position"]]
        state["messages"].append({"role": "assistant", "content": current_message})
        state["next_node"] = "update_conversation_stream"
        return ConversationState(**state)

    except Exception as e:
        logger.error(f"General error: {str(e)}")
        logger.exception("Full stack trace:")
        error_message = f"[대화 생성 오류] {str(e)}"

        state["messages"].append({"role": "assistant", "content": error_message})
        state["response"] = error_message
        return ConversationState(**state)


def update_conversation_stream(state: ConversationState) -> ConversationState:
    try:
        streaming = state["streaming"]
        if streaming["is_complete"]:
            return state

        chunk_size = 20
        current_pos = streaming["current_position"]
        next_pos = min(current_pos + chunk_size, len(streaming["message"]))
        streaming["current_position"] = next_pos
        streaming["is_complete"] = next_pos >= len(streaming["message"])
        current_message = streaming["message"][:next_pos]
        state["messages"][-1]["content"] = current_message
        state["next_node"] = "update_conversation_stream"
        time.sleep(1)
        return state

    except Exception as e:
        return state
