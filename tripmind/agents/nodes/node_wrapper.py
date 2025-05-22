import logging
import traceback
import inspect
from typing import Dict, Any, Callable, TypeVar, cast
from functools import wraps

from tripmind.utils.guardrails import validate_node_state, validate_node_response
from tripmind.utils.response_monitor import response_monitor

logger = logging.getLogger(__name__)

# 제네릭 타입 정의
T = TypeVar("T", bound=Dict[str, Any])


def node_wrapper(func: Callable[[Any, T], T]) -> Callable[[Any, T], T]:
    """
    LangGraph 노드 함수를 감싸서 공통 검증 및 오류 처리 적용

    Args:
        func: 원본 노드 함수

    Returns:
        래핑된 노드 함수
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        # 노드 이름 추출
        node_name = func.__name__

        # 함수 시그니처에서 상태 파라미터 위치 찾기
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())

        # 첫 번째 인자는 일반적으로 LLM, 두 번째가 상태
        state_idx = 1 if len(param_names) > 1 else 0

        # 상태 객체 접근
        if len(args) > state_idx:
            state = args[state_idx]
        else:
            state = kwargs.get(param_names[state_idx], {})

        # 상태가 없는 경우 처리
        if not state:
            logger.error(f"{node_name}: 상태 객체가 없음")
            return cast(T, {"error": "상태 객체 없음", "messages": []})

        try:
            # 진입 로그
            logger.info(
                f"{node_name} 시작: user_input={state.get('user_input', '')[:30]}..."
            )
            # 세션 ID 추출
            config = state.get("config_data", {})
            session_id = config.get("thread_id", "default")

            # 상태 검증
            validated_state = validate_node_state(state)

            # 원본 함수 호출
            if len(args) > state_idx:
                # 검증된 상태로 args 업데이트
                args_list = list(args)
                args_list[state_idx] = validated_state
                result = func(*args_list, **kwargs)
            else:
                # kwargs에 검증된 상태 적용
                kwargs[param_names[state_idx]] = validated_state
                result = func(**kwargs)

            # 결과 검증
            if not isinstance(result, dict):
                logger.error(f"{node_name}: 결과가 딕셔너리가 아님: {type(result)}")
                return cast(T, {"error": "결과 형식 오류", "messages": []})

            if "response" not in result:
                # 1. messages에서 assistant 메시지가 있는 경우
                if "messages" in result and isinstance(result["messages"], list):
                    assistant_messages = [
                        msg
                        for msg in result["messages"]
                        if msg.get("role") == "assistant"
                    ]
                    if assistant_messages:
                        # 마지막 assistant 메시지를 응답으로 설정
                        result["response"] = assistant_messages[-1]["content"]
                        logger.info(
                            f"{node_name}: assistant 메시지에서 response 필드 자동 설정"
                        )
                # 2. input_node처럼 user_input만 있는 경우
                elif "user_input" in result:
                    # user_input을 response로 설정 (또는 필요한 값으로 설정)
                    result["response"] = result.get("user_input", "")
                    logger.info(f"{node_name}: user_input에서 response 필드 자동 설정")

            # 응답이 있는 경우 검증
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
                    # 응답 모니터링 및 분석
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

                        # 감지된 이슈를 상태에 기록
                        if "monitoring" not in result:
                            result["monitoring"] = {}
                        result["monitoring"][node_name] = monitor_result

                    # 가드레일 응답 검증 및 수정
                    original_response = assistant_message["content"]
                    result["response"] = validate_node_response(
                        node_name, assistant_message["content"]
                    )

                    # 응답이 수정되었는지 확인
                    if original_response != result["response"]:
                        logger.info(f"{node_name} 응답이 가드레일에 의해 수정됨")

                    # 메시지도 업데이트
                    if "messages" in result and result["messages"]:
                        for i, msg in enumerate(result["messages"]):
                            if msg.get("role") == "assistant" and msg.get(
                                "content"
                            ) == state.get("response"):
                                result["messages"][i]["content"] = result["response"]

            # 성공 로그
            logger.info(f"{node_name} 완료")
            return cast(T, result)

        except Exception as e:
            # 오류 로그
            logger.error(f"{node_name} 오류: {str(e)}")
            logger.debug(traceback.format_exc())

            # 기본 오류 응답
            error_message = f"[{node_name} 오류] {str(e)}"

            # 기존 상태 유지하면서 오류 정보 추가
            error_state = dict(state)
            if "messages" not in error_state:
                error_state["messages"] = []

            # 오류 메시지 추가
            error_state["messages"].append(
                {"role": "assistant", "content": error_message}
            )

            # 응답 필드 업데이트
            error_state["response"] = error_message
            error_state["error"] = str(e)

            return cast(T, error_state)

    return wrapper
