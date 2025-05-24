import logging

from tripmind.agents.sharing.utils.extract_info import extract_share_request
from tripmind.agents.sharing.utils.validator import validate_share_request
from tripmind.services.sharing.sharing_service import sharing_service
from tripmind.agents.sharing.types.sharing_state_type import SharingRouterState

logger = logging.getLogger(__name__)


def sharing_node(state: SharingRouterState) -> SharingRouterState:
    try:
        user_input = state.get("user_input")
        context = state.get("context", {})
        share_request = extract_share_request(user_input)

        if "messages" not in state:
            state["messages"] = []

        share_request = context.get("share_request")
        share_request = validate_share_request(share_request)

        itinerary_id = context.get("itinerary_id")

        if not itinerary_id:
            logger.warning("공유 요청이 있지만 일정 ID가 없음")
            response = (
                "일정을 먼저 생성해주세요. 그 후에 공유 기능을 사용할 수 있습니다."
            )
            return SharingRouterState(
                user_input=user_input,
                messages=state["messages"],
                context=context,
                response=response,
                next_node="sharing_node",
            )

        share_type = share_request["share_type"]
        days = share_request["days"]
        share_method = share_request.get("share_method")

        base_url = context.get("base_url")

        share_type_text = "읽기 전용" if share_type == "VIEW" else "편집 가능"
        response = (
            f"네, {days}일 동안 유효한 {share_type_text} 공유 링크를 생성했습니다."
        )

        if share_method:
            if share_method == "KAKAO":
                response += " 카카오톡으로 친구들에게 공유할 수 있습니다."
            elif share_method == "EMAIL":
                response += " 이메일로 공유할 수 있습니다."
            elif share_method == "SMS":
                response += " 문자 메시지로 공유할 수 있습니다."
        else:
            response += " 이 링크를 통해 다른 사람들과 여행 일정을 공유할 수 있습니다."

        api_result = sharing_service.create_share_link_api(
            itinerary_id, share_type, days, base_url
        )

        if api_result.get("success", False):
            share_data = api_result.get("data", {})
            share_url = share_data.get("share_url")
            expires_at = share_data.get("expires_at")

            if share_url:
                response += f"\n\n📤 공유 링크: {share_url}"
                if not share_url.startswith(("http://", "https://")):
                    logger.warning(f"올바르지 않은 URL 형식: {share_url}")
                    response += "\n\n(주의: 링크가 올바른 형식이 아닙니다. 관리자에게 문의하세요.)"

            if expires_at:
                response += f"\n만료일: {expires_at}"
        else:
            error = api_result.get("error", "알 수 없는 오류")
            logger.error(f"공유 링크 생성 실패: {error}")
            response += (
                f"\n\n공유 링크 생성 중 오류가 발생했습니다. 나중에 다시 시도해주세요."
            )

        state["messages"].append({"role": "assistant", "content": response})

        context["share_info"] = {
            "share_type": share_type,
            "days": days,
            "share_method": share_method,
            "created_at": api_result.get("data", {}).get("created_at", ""),
            "status": "success" if api_result.get("success", False) else "failed",
        }

        logger.info(f"공유 응답 생성 완료: {len(response)} 글자")

        return SharingRouterState(
            user_input=user_input,
            messages=state["messages"],
            context=context,
            response=response,
            next_node="sharing_node",
        )

    except Exception as e:
        logger.error(f"공유 노드 처리 오류: {str(e)}")
        logger.exception("전체 오류:")

        raise e
