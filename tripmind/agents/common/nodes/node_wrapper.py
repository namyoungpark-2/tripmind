import logging
import traceback
import inspect
from typing import Dict, Any, Callable, TypeVar, cast
from functools import wraps

from tripmind.utils.guardrails import validate_node_state, validate_node_response
from tripmind.utils.response_monitor import response_monitor

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Dict[str, Any])


def node_wrapper(func: Callable[[Any, T], T]) -> Callable[[Any, T], T]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        node_name = func.__name__

        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        state_idx = 1 if len(param_names) > 1 else 0

        if len(args) > state_idx:
            state = args[state_idx]
        else:
            state = kwargs.get(param_names[state_idx], {})

        if not state:
            logger.error(f"{node_name}: 상태 객체가 없음")
            return cast(T, {"error": "상태 객체 없음", "messages": []})

        try:
            logger.info(
                f"{node_name} 시작: user_input={state.get('user_input', '')[:30]}..."
            )
            config = state.get("config_data", {})
            session_id = config.get("thread_id", "default")

            validated_state = validate_node_state(state)

            if len(args) > state_idx:
                args_list = list(args)
                args_list[state_idx] = validated_state
                result = func(*args_list, **kwargs)
            else:
                kwargs[param_names[state_idx]] = validated_state
                result = func(**kwargs)

            # Tool 선택 정보 로깅
            if hasattr(result, "tool_calls") and result.tool_calls:
                print(f"Selected Tools: {[tool.name for tool in result.tool_calls]}")
            elif isinstance(result, dict) and "tool_calls" in result:
                print(
                    f"Selected Tools: {[tool['name'] for tool in result['tool_calls']]}"
                )

            if not isinstance(result, dict):
                logger.error(f"{node_name}: 결과가 딕셔너리가 아님: {type(result)}")
                return cast(T, {"error": "결과 형식 오류", "messages": []})

            if "response" not in result:
                if "messages" in result and isinstance(result["messages"], list):
                    assistant_messages = [
                        msg
                        for msg in result["messages"]
                        if msg.get("role") == "assistant"
                    ]
                    if assistant_messages:
                        result["response"] = assistant_messages[-1]["content"]
                        logger.info(
                            f"{node_name}: assistant 메시지에서 response 필드 자동 설정"
                        )
                elif "user_input" in result:
                    result["response"] = result.get("user_input", "")
                    logger.info(f"{node_name}: user_input에서 response 필드 자동 설정")

            if "messages" in result and isinstance(result["messages"], list):
                assistant_message = next(
                    (
                        msg
                        for msg in result["messages"]
                        if msg.get("role") == "assistant"
                    ),
                    None,
                )
                if assistant_message:
                    monitor_result = response_monitor.analyze_and_log(
                        response=assistant_message["content"],
                        node_name=node_name,
                        session_id=session_id,
                    )

                    if monitor_result and monitor_result.get("issues"):
                        num_issues = len(monitor_result["issues"])
                        logger.warning(
                            f"{node_name} 응답에서 {num_issues}개 이슈 감지됨"
                        )

                        if "monitoring" not in result:
                            result["monitoring"] = {}
                        result["monitoring"][node_name] = monitor_result

                    original_response = assistant_message["content"]
                    result["response"] = validate_node_response(
                        node_name, assistant_message["content"]
                    )

                    if original_response != result["response"]:
                        logger.info(f"{node_name} 응답이 가드레일에 의해 수정됨")

                    if "messages" in result and result["messages"]:
                        for i, msg in enumerate(result["messages"]):
                            if msg.get("role") == "assistant" and msg.get(
                                "content"
                            ) == state.get("response"):
                                result["messages"][i]["content"] = result["response"]

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

    return wrapper
