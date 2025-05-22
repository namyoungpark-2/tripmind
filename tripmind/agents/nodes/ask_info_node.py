from typing import Dict, Any

def ask_info_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """추가 정보 요청 노드"""
    missing = []
    if not state.get("destination"):
        missing.append("목적지")
    if not state.get("duration"):
        missing.append("여행 기간")
    
    msg = f"여행 일정을 만들기 위해 {', '.join(missing)}에 대한 정보가 필요합니다. 알려주실 수 있나요?"
    
    state["messages"].append({
        "role": "assistant",
        "content": msg
    })
    
    return state