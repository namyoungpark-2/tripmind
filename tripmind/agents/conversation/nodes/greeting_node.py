from pathlib import Path
import logging
import time

from tripmind.services.prompt.prompt_service import prompt_service
from tripmind.agents.conversation.types.conversation_state_type import ConversationState
from tripmind.services.session.session_manage_service import session_manage_service

PROMPT_DIR = Path(__file__).parent / "../prompt_templates"

logger = logging.getLogger(__name__)


def greeting_node(state: ConversationState) -> ConversationState:
    user_input = state.get("user_input", "")
    session_id = state.get("config_data", {}).get("thread_id", "default")
    greeting_msg = prompt_service.get_string_prompt(PROMPT_DIR / "greeting" / "v1.yaml")

    state["streaming"] = {
        "message": greeting_msg,
        "current_position": 0,
        "is_complete": False,
    }

    current_message = greeting_msg[: state["streaming"]["current_position"]]
    state["messages"].append(
        {
            "role": "assistant",
            "content": current_message,
        }
    )
    state["next_node"] = "update_greeting_stream"

    memory = session_manage_service.get_session_memory(
        session_id,
        memory_key="chat_history",
        input_key="input",
        output_key="output",
    )
    memory.save_context(
        inputs={memory.input_key: user_input},
        outputs={memory.output_key: greeting_msg},
    )
    state = ConversationState(**state)
    return state


def update_greeting_stream(state: ConversationState) -> ConversationState:
    try:
        if "streaming" not in state:
            state["streaming"] = {
                "message": "안녕하세요! 트립마인드입니다.",
                "current_position": 0,
                "is_complete": False,
            }
            return state
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
        state["next_node"] = "update_greeting_stream"
        time.sleep(1)  # 1초 대기
        return state
    except Exception as e:
        return state
