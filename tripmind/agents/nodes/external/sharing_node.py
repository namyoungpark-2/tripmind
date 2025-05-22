import re
import logging
import requests
from typing import Dict, Any, Optional
from urllib.parse import urljoin
from langchain_anthropic import ChatAnthropic

logger = logging.getLogger(__name__)

def extract_share_request(text: str) -> Optional[Dict[str, Any]]:
    """
    텍스트에서 일정 공유 요청 추출
    
    Args:
        text: 사용자 메시지
        
    Returns:
        공유 요청 정보 (공유 유형, 기간 등) 또는 None
    """
    # 공유 요청 여부 확인
    share_patterns = [
        r'일정[\s]*(?:공유|공개)[\s]*(해줘|해 줘|할래|하자|부탁해|부탁|좀)',
        r'(?:공유|공개)[\s]*(?:링크|URL)[\s]*(?:만들어|생성|줘|좀)',
        r'(?:친구|가족|같이|동료)[\s]*(?:에게|한테|와|과|랑)[\s]*(?:공유|보여|전달)',
        r'url[\s]*(?:생성|만들어|보내)',
        r'공유[\s]*(?:하고 싶어|하고싶어|하고 싶|하고싶|좀)',
        r'링크[\s]*(?:만들어|생성|보내|줘|주세요)',
        r'(?:카톡|카카오톡|메일|이메일|문자)[\s]*(?:으로|로)[\s]*(?:공유|보내|전송|전달)',
        r'(?:카톡|카카오톡|메일|이메일|문자)[\s]*보내',
        r'일정[\s]*(?:내보내|외부|밖으로|보내)',
    ]
    
    is_share_request = False
    matched_pattern = None
    
    for pattern in share_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            is_share_request = True
            matched_pattern = match.group(0)
            break
            
    if not is_share_request:
        return None
    
    logger.info(f"공유 요청 감지: '{matched_pattern}' 패턴으로 인식")
    
    # 공유 유형 확인 (읽기 전용 vs 편집 가능)
    share_type = 'VIEW'  # 기본값
    if re.search(r'(?:수정|편집|변경|업데이트)[\s]*(?:가능|할 수|허용|권한)', text, re.IGNORECASE):
        share_type = 'EDIT'
        logger.info("편집 가능한 공유 요청 감지")
    
    # 공유 기간 추출
    days = 7  # 기본값
    duration_match = re.search(r'(\d+)[\s]*(?:일|날짜|기간|day)', text, re.IGNORECASE)
    if duration_match:
        days = int(duration_match.group(1))
        # 상식적인 범위로 제한
        days = min(max(1, days), 30)
        logger.info(f"공유 기간 설정: {days}일")
    
    # 공유 방식 추출 (카카오톡, 이메일 등)
    share_method = None
    if re.search(r'(?:카톡|카카오톡)', text, re.IGNORECASE):
        share_method = 'KAKAO'
    elif re.search(r'(?:메일|이메일|email)', text, re.IGNORECASE):
        share_method = 'EMAIL'
    elif re.search(r'(?:문자|SMS|메시지)', text, re.IGNORECASE):
        share_method = 'SMS'
    
    return {
        "share_type": share_type,
        "days": days,
        "share_method": share_method,
        "matched_pattern": matched_pattern
    }

def validate_share_request(share_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    공유 요청 유효성 검사 및 정규화
    
    Args:
        share_info: 공유 요청 정보
        
    Returns:
        검증된 공유 요청 정보
    """
    # 딥카피 필요
    validated = {**share_info}
    
    # 공유 유형 검증
    if validated.get('share_type') not in ['VIEW', 'EDIT']:
        logger.warning(f"잘못된 공유 유형: {validated.get('share_type')}, 기본값 VIEW로 설정")
        validated['share_type'] = 'VIEW'
        
    # 공유 기간 검증
    try:
        days = int(validated.get('days', 7))
        if days < 1:
            logger.warning(f"공유 기간이 너무 짧음: {days}일, 최소 1일로 설정")
            days = 1
        elif days > 30:
            logger.warning(f"공유 기간이 너무 김: {days}일, 최대 30일로 제한")
            days = 30
        validated['days'] = days
    except (ValueError, TypeError):
        logger.warning(f"잘못된 공유 기간 형식: {validated.get('days')}, 기본값 7일로 설정")
        validated['days'] = 7
        
    # 공유 방식 검증
    if validated.get('share_method') not in [None, 'KAKAO', 'EMAIL', 'SMS']:
        logger.warning(f"잘못된 공유 방식: {validated.get('share_method')}, None으로 설정")
        validated['share_method'] = None
        
    return validated

def create_share_link_api(itinerary_id: int, share_type: str, days: int, base_url: str = None) -> Dict[str, Any]:
    """
    API를 통해 실제 공유 링크 생성
    
    Args:
        itinerary_id: 일정 ID
        share_type: 공유 유형 (VIEW/EDIT)
        days: 공유 기간 (일)
        base_url: API 기본 URL
        
    Returns:
        공유 정보 (성공 여부, 링크 등)
    """
    try:
        # 일정 ID 검증
        if not itinerary_id or not isinstance(itinerary_id, int):
            logger.error(f"잘못된 일정 ID: {itinerary_id}")
            return {
                "success": False,
                "error": f"유효하지 않은 일정 ID: {itinerary_id}"
            }
            
        # 공유 유형 검증
        if share_type not in ['VIEW', 'EDIT']:
            logger.warning(f"잘못된 공유 유형: {share_type}, VIEW로 기본 설정")
            share_type = 'VIEW'
            
        # 공유 기간 검증
        try:
            days = int(days)
            if days < 1 or days > 30:
                logger.warning(f"공유 기간이 범위를 벗어남: {days}일, 7일로 설정")
                days = 7
        except (ValueError, TypeError):
            logger.warning(f"잘못된 공유 기간: {days}, 7일로 설정")
            days = 7
            
        # API 기본 URL 설정
        api_url = urljoin(base_url or "http://localhost:8000", f"/api/tripmind/itinerary/{itinerary_id}/public/")
        
        # API 요청 데이터
        data = {
            "is_public": True,
            "share_type": share_type,
            "expires_in_days": days
        }
        
        # API 호출
        logger.info(f"공유 링크 생성 API 호출: {api_url}")
        response = requests.post(api_url, json=data)
        
        # 응답 확인
        if response.status_code == 200 or response.status_code == 201:
            logger.info("공유 링크 생성 성공")
            return {
                "success": True,
                "data": response.json(),
                "status_code": response.status_code
            }
        else:
            logger.error(f"공유 링크 생성 실패: {response.status_code}, {response.text}")
            return {
                "success": False,
                "error": f"API 오류: {response.status_code}",
                "status_code": response.status_code
            }
    except Exception as e:
        logger.exception(f"공유 링크 생성 API 호출 중 예외 발생: {str(e)}")
        return {
            "success": False,
            "error": f"API 호출 오류: {str(e)}"
        }

def handle_share_request(user_input: str, response: str, context: Dict[str, Any], base_url: str = None) -> str:
    """
    일정 공유 요청 처리 및 응답 생성
    
    Args:
        user_input: 사용자 입력
        response: 기존 AI 응답
        context: 컨텍스트 정보
        base_url: API 기본 URL
        
    Returns:
        공유 정보가 포함된 응답
    """
    share_info = extract_share_request(user_input)
    if not share_info:
        return response
    
    itinerary_id = context.get("itinerary_id")
    if not itinerary_id:
        logger.warning("공유 요청이 있지만 일정 ID가 없음")
        return response + "\n\n일정을 먼저 생성해주세요. 그 후에 공유 기능을 사용할 수 있습니다."
    
    # 공유 요청 검증
    share_info = validate_share_request(share_info)
    
    share_type = share_info["share_type"]
    days = share_info["days"]
    share_method = share_info.get("share_method")
    
    # API 호출을 통한 실제 공유 링크 생성
    api_result = create_share_link_api(itinerary_id, share_type, days, base_url)
    
    if api_result.get("success", False):
        # API 호출 성공 시 실제 URL 사용
        share_data = api_result.get("data", {})
        share_url = share_data.get("share_url", f"http://localhost:8000/api/tripmind/share/itinerary/{itinerary_id}/")
        expires_at = share_data.get("expires_at", "")
        
        # 공유 방식에 따른 추가 안내
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
        # API 호출 실패 시 기본 정보만 제공
        error = api_result.get("error", "알 수 없는 오류")
        logger.error(f"공유 링크 생성 실패: {error}")
        
        share_type_text = "읽기 전용" if share_type == "VIEW" else "편집 가능"
        
        share_message = f"\n\n📤 **일정 공유 정보**\n"
        share_message += f"- 공유 유형: {share_type_text}\n"
        share_message += f"- 유효 기간: {days}일\n"
        share_message += f"- 공유 ID: {itinerary_id}\n\n"
        share_message += "앱에서 직접 공유 링크를 생성하여 친구들과 일정을 공유할 수 있습니다."
    
    return response + share_message

def sharing_node(llm: ChatAnthropic, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    공유 노드 - 일정 공유 요청 처리
    
    Args:
        llm: 언어 모델
        state: 상태 정보
        
    Returns:
        업데이트된 상태
    """
    try:
        # 입력 데이터 구성
        user_input = state.get("user_input", "")
        context = state.get("context", {})
        
        # 키 없이도 안전하게 접근하기 위해 초기화
        if "messages" not in state:
            state["messages"] = []
        
        # 공유 요청 여부 확인
        share_request = extract_share_request(user_input)
        if not share_request:
            # 공유 요청이 없으면 빈 응답 반환 (다음 노드로 전달)
            logger.info("공유 요청 없음, 다음 노드로 전달")
            return state
            
        # 공유 요청 검증
        share_request = validate_share_request(share_request)
        
        # 일정 ID 확인
        itinerary_id = context.get("itinerary_id")
        if not itinerary_id:
            logger.warning("공유 요청이 있지만 일정 ID가 없음")
            response = "일정을 먼저 생성해주세요. 그 후에 공유 기능을 사용할 수 있습니다."
            
            # 응답 저장
            state["messages"].append({"role": "assistant", "content": response})
            
            return {**state, "response": response}
        
        # 공유 유형과 기간
        share_type = share_request["share_type"]
        days = share_request["days"]
        share_method = share_request.get("share_method")
        
        # API 기본 URL (컨텍스트에서 가져오기)
        base_url = context.get("base_url")
        
        # 응답 생성
        share_type_text = "읽기 전용" if share_type == "VIEW" else "편집 가능"
        response = f"네, {days}일 동안 유효한 {share_type_text} 공유 링크를 생성했습니다."
        
        # 공유 방식에 따른 추가 안내
        if share_method:
            if share_method == "KAKAO":
                response += " 카카오톡으로 친구들에게 공유할 수 있습니다."
            elif share_method == "EMAIL":
                response += " 이메일로 공유할 수 있습니다."
            elif share_method == "SMS":
                response += " 문자 메시지로 공유할 수 있습니다."
        else:
            response += " 이 링크를 통해 다른 사람들과 여행 일정을 공유할 수 있습니다."
            
        # API 호출 (실제 링크 생성)
        api_result = create_share_link_api(itinerary_id, share_type, days, base_url)
        
        if api_result.get("success", False):
            # API 호출 성공 시 실제 URL 추가
            share_data = api_result.get("data", {})
            share_url = share_data.get("share_url")
            expires_at = share_data.get("expires_at")
            
            if share_url:
                response += f"\n\n📤 공유 링크: {share_url}"
                # 유효성 검사를 위한 URL 형식 확인
                if not share_url.startswith(('http://', 'https://')):
                    logger.warning(f"올바르지 않은 URL 형식: {share_url}")
                    response += "\n\n(주의: 링크가 올바른 형식이 아닙니다. 관리자에게 문의하세요.)"
                    
            if expires_at:
                response += f"\n만료일: {expires_at}"
        else:
            # API 호출 실패 시 오류 정보 추가
            error = api_result.get("error", "알 수 없는 오류")
            logger.error(f"공유 링크 생성 실패: {error}")
            response += f"\n\n공유 링크 생성 중 오류가 발생했습니다. 나중에 다시 시도해주세요."
        
        # 응답 저장
        state["messages"].append({"role": "assistant", "content": response})
        
        # 컨텍스트에 공유 정보 저장
        context["share_info"] = {
            "share_type": share_type,
            "days": days,
            "share_method": share_method,
            "created_at": api_result.get("data", {}).get("created_at", ""),
            "status": "success" if api_result.get("success", False) else "failed"
        }
        
        # 응답 로깅
        logger.info(f"공유 응답 생성 완료: {len(response)} 글자")
        
        return {**state, "context": context, "response": response, "share_request": share_request}
        
    except Exception as e:
        logger.error(f"공유 노드 처리 오류: {str(e)}")
        logger.exception("전체 오류:")
        
        error_message = f"공유 기능 처리 중 오류가 발생했습니다: {str(e)}"
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({"role": "assistant", "content": error_message})
        
        return {**state, "response": error_message}