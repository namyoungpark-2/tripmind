import requests
from typing import Dict, Any
from urllib.parse import urljoin
import logging
from tripmind.agents.sharing.utils.extract_info import extract_share_request
from tripmind.agents.sharing.utils.validator import validate_share_request

logger = logging.getLogger(__name__)


class SharingService:
    def create_share_link_api(
        self,
        itinerary_id: int,
        share_type: str,
        days: int,
        base_url: str = None,
    ) -> Dict[str, Any]:
        try:
            if not itinerary_id or not isinstance(itinerary_id, int):
                logger.error(f"잘못된 일정 ID: {itinerary_id}")
                return {
                    "success": False,
                    "error": f"유효하지 않은 일정 ID: {itinerary_id}",
                }

            if share_type not in ["VIEW", "EDIT"]:
                logger.warning(f"잘못된 공유 유형: {share_type}, VIEW로 기본 설정")
                share_type = "VIEW"

            try:
                days = int(days)
                if days < 1 or days > 30:
                    logger.warning(f"공유 기간이 범위를 벗어남: {days}일, 7일로 설정")
                    days = 7
            except (ValueError, TypeError):
                logger.warning(f"잘못된 공유 기간: {days}, 7일로 설정")
                days = 7

            api_url = urljoin(
                base_url or "http://localhost:8000/",
                f"/api/tripmind/itinerary/{itinerary_id}/public/",
            )

            data = {
                "is_public": True,
                "share_type": share_type,
                "expires_in_days": days,
            }

            logger.info(f"공유 링크 생성 API 호출: {api_url}")
            response = requests.post(api_url, json=data)

            if response.status_code == 200 or response.status_code == 201:
                logger.info("공유 링크 생성 성공")
                return {
                    "success": True,
                    "data": response.json(),
                    "status_code": response.status_code,
                }
            else:
                logger.error(
                    f"공유 링크 생성 실패: {response.status_code}, {response.text}"
                )
                return {
                    "success": False,
                    "error": f"API 오류: {response.status_code}",
                    "status_code": response.status_code,
                }
        except Exception as e:
            logger.exception(f"공유 링크 생성 API 호출 중 예외 발생: {str(e)}")
            return {"success": False, "error": f"API 호출 오류: {str(e)}"}

    def get_share_request(
        user_input: str, response: str, context: Dict[str, Any], base_url: str = None
    ) -> str:
        share_info = extract_share_request(user_input)
        if not share_info:
            return response

        itinerary_id = context.get("itinerary_id")
        if not itinerary_id:
            logger.warning("공유 요청이 있지만 일정 ID가 없음")
            return (
                response
                + "\n\n일정을 먼저 생성해주세요. 그 후에 공유 기능을 사용할 수 있습니다."
            )

        share_info = validate_share_request(share_info)

        share_type = share_info["share_type"]
        days = share_info["days"]
        share_method = share_info.get("share_method")

        api_result = sharing_service.create_share_link_api(
            itinerary_id, share_type, days, base_url
        )

        if api_result.get("success", False):
            share_data = api_result.get("data", {})
            share_url = share_data.get(
                "share_url",
                f"http://localhost:8000/api/tripmind/share/itinerary/{itinerary_id}/",
            )
            expires_at = share_data.get("expires_at", "")

            method_info = ""
            if share_method == "KAKAO":
                method_info = "\n\n카카오톡으로 공유하려면 위 링크를 복사하여 대화방에 붙여넣기 하시면 됩니다."
            elif share_method == "EMAIL":
                method_info = "\n\n이메일로 공유하려면 위 링크를 복사하여 메일에 붙여넣기 하시면 됩니다."
            elif share_method == "SMS":
                method_info = "\n\n문자로 공유하려면 위 링크를 복사하여 메시지에 붙여넣기 하시면 됩니다."

            share_type_text = "읽기 전용" if share_type == "VIEW" else "편집 가능"

            share_message = f"\n\n📤 **일정 공유 링크가 생성되었습니다!**\n"
            share_message += f"- 공유 링크: {share_url}\n"
            share_message += f"- 공유 유형: {share_type_text}\n"
            share_message += f"- 유효 기간: {days}일"
            if expires_at:
                share_message += f" (만료일: {expires_at})"
            share_message += f"{method_info}\n\n"
            share_message += "이 링크를 통해 친구들과 일정을 공유할 수 있습니다."
        else:
            error = api_result.get("error", "알 수 없는 오류")
            logger.error(f"공유 링크 생성 실패: {error}")

            share_type_text = "읽기 전용" if share_type == "VIEW" else "편집 가능"

            share_message = f"\n\n📤 **일정 공유 정보**\n"
            share_message += f"- 공유 유형: {share_type_text}\n"
            share_message += f"- 유효 기간: {days}일\n"
            share_message += f"- 공유 ID: {itinerary_id}\n\n"
            share_message += (
                "앱에서 직접 공유 링크를 생성하여 친구들과 일정을 공유할 수 있습니다."
            )

        return response + share_message


sharing_service = SharingService()
