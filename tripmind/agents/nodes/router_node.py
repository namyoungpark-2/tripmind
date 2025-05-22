from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    라우팅 노드
    
    input_node에서 결정된 next_node 값을 기반으로 실제 라우팅 경로 결정
    
    Args:
        state: 현재 상태
        
    Returns:
        다음 노드 정보가 포함된 상태 객체
    """
    # next_node 필드 확인
    next_node = state.get("next_node")
    
    # 로깅
    logger.info(f"라우팅: {next_node} 노드로 이동 (의도: {state.get('intent', '알수없음')})")
    
    # next_node가 없으면 기본값으로 대화 노드 사용
    if not next_node:
        logger.warning("next_node 값이 없음, 기본값(conversation)으로 설정")
        state["next_node"] = "conversation"
        
    # backward compatibility를 위한 next 필드도 설정
    state["next"] = state["next_node"]
    
    return state