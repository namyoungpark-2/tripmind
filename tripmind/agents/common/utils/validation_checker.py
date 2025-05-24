from tripmind.agents.common.types.base_state_type import BaseState


def should_continue_streaming(state: BaseState) -> bool:
    streaming = state.get("streaming", {})
    return not streaming.get("is_complete", False)
