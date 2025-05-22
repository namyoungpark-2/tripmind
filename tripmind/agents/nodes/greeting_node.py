from typing import Dict, Any

def greeting_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """인사 노드"""
    greeting_msg = "안녕하세요! 트립마인드입니다. 어떤 여행을 계획 중이신가요? 목적지와 일정 등을 알려주시면 도와드리겠습니다."
    
    state["messages"].append({
        "role": "assistant",
        "content": greeting_msg
    })
    
    return state
