from tripmind.agents.prompt_router.types.prompt_router_state_type import (
    PromptRouterState,
)
from tripmind.agents.prompt_router.intent.manager import intent_pattern_manager
from tripmind.agents.prompt_router.constants.intent_constants import INTENT_TO_NODE_MAP


def input_node(state: PromptRouterState) -> PromptRouterState:
    user_input = state.get("user_input", "")
    context = state.get("context", {})
    message = state.get("messages", [])
    message.append({"role": "user", "content": user_input})

    intent = intent_pattern_manager.determine_intent_by_rule_based(user_input)
    next_node = INTENT_TO_NODE_MAP.get(intent, "conversation")

    return PromptRouterState(
        user_input=user_input,
        messages=message,
        context=context,
        response=user_input,
        next_node=next_node,
        intent=intent,
    )
