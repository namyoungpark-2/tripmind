import logging
import traceback
import inspect
from typing import Dict, Any, Callable, TypeVar, cast
from functools import wraps

from tripmind.guardrails.node_validator import NodeValidator
from tripmind.utils.response_monitor import response_monitor

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Dict[str, Any])


def node_wrapper(func: Callable[[Any, T], T]) -> Callable[[Any, T], T]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        node_name = func.__name__

        state = _extract_state(func, args, kwargs)

        if not state:
            logger.error(f"{node_name}: 상태 객체가 없음")
            return cast(T, {"error": "상태 객체 없음", "messages": []})

        try:
            logger.info(
                f"{node_name} 시작: user_input={state.get('user_input', '')[:30]}..."
            )
            config = state.get("config_data", {})
            session_id = config.get("thread_id", "default")

            validated_state = NodeValidator.validate_state(state)

            result = _call_func_with_state(func, args, kwargs, validated_state)

            if not isinstance(result, dict):
                logger.error(f"{node_name}: 결과가 딕셔너리가 아님: {type(result)}")
                return cast(T, {"error": "결과 형식 오류", "messages": []})

            _monitor_response_and_validate(result, node_name, session_id, state)

            logger.info(f"{node_name} 완료")
            return cast(T, result)

        except Exception as e:
            logger.error(f"{node_name} 오류: {str(e)}")
            logger.debug(traceback.format_exc())

            error_message = f"[{node_name} 오류] {str(e)}"

            error_state = dict(state)
            if "messages" not in error_state:
                error_state["messages"] = []

            error_state["messages"].append(
                {"role": "assistant", "content": error_message}
            )

            error_state["response"] = error_message
            error_state["error"] = str(e)

            return cast(T, error_state)

    def _extract_state(func: Callable, args, kwargs) -> Dict[str, Any]:
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        state_idx = 1 if len(param_names) > 1 else 0
        if len(args) > state_idx:
            return args[state_idx]

    def _call_func_with_state(func, args, kwargs, validated_state):
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        state_idx = 1 if len(param_names) > 1 else 0

        if len(args) > state_idx:
            args_list = list(args)
            args_list[state_idx] = validated_state
            return func(*args_list, **kwargs)
        else:
            kwargs[param_names[state_idx]] = validated_state
            return func(**kwargs)

    def _monitor_response_and_validate(
        result: Dict[str, Any],
        node_name: str,
        session_id: str,
        original_state: Dict[str, Any],
    ):
        messages = result.get("messages", [])
        if not isinstance(messages, list):
            return

        assistant_msg = next(
            (m for m in messages if m.get("role") == "assistant"), None
        )
        if not assistant_msg:
            return

        content = assistant_msg.get("content", "")
        monitor_result = response_monitor.analyze_and_log(
            content, node_name, session_id
        )

        if monitor_result and monitor_result.get("issues"):
            logger.warning(
                f"{node_name} 응답에서 {len(monitor_result['issues'])}개 이슈 감지됨"
            )
            result.setdefault("monitoring", {})[node_name] = monitor_result

        validated_response = NodeValidator.validate_response_for_node(
            node_name, content
        )
        if validated_response != content:
            logger.info(f"{node_name} 응답이 가드레일에 의해 수정됨")

        result["response"] = validated_response

        for msg in messages:
            if msg.get("role") == "assistant" and msg.get(
                "content"
            ) == original_state.get("response"):
                msg["content"] = validated_response

    # def _ensure_response_field(result: Dict[str, Any]):
    #   if "response" not in result:
    #     if "messages" in result and isinstance(result["messages"], list):
    #         assistant_msgs = [m for m in result["messages"] if m.get("role") == "assistant"]
    #         if assistant_msgs:
    #             result["response"] = assistant_msgs[-1]["content"]
    #             logger.info("assistant 메시지에서 response 필드 자동 설정")
    #     elif "user_input" in result:
    #         result["response"] = result.get("user_input", "")
    #         logger.info("user_input에서 response 필드 자동 설정")

    return wrapper
