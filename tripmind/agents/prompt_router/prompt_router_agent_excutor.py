# tripmind/agents/excutors/prompt_router_agent_excutor.py
import json
from typing import Dict, Any


from ..base_agent_excutor import BaseAgentExcutor
from .types.prompt_router_state_type import PromptRouterState
from .constants.intent_constants import (
    Intent,
    INTENT_DESCRIPTIONS,
    INTENT_TO_NODE_MAP,
)
from tripmind.llm.prompt_loader import prompt_loader
from .prompt_router_agent_llm import prompt_router_agent_llm


class PromptRouterAgentExcutor(BaseAgentExcutor):
    """
    사용자 입력의 목적(intent)을 분류하는 에이전트 실행기
    """

    def __init__(self):
        # 프롬프트 템플릿 생성 (상수에서 의도 설명 가져옴)
        intent_descriptions = "\n".join(
            [
                f"- {intent.value}: {description}"
                for intent, description in INTENT_DESCRIPTIONS.items()
            ]
        )

        prompt = prompt_loader.get_prompt_template(
            "prompt_router/v1.yaml",
            {
                "intent_descriptions": intent_descriptions,
                "model": prompt_router_agent_llm.get_llm().model,
            },
        )

        # LLMChain 대신 RunnableSequence(|) 사용
        self.chain = prompt | prompt_router_agent_llm.get_llm()

    def process_prompt(
        self,
        prompt: str,
        session_id: str = "default",
        start_node: str = "conversation",
    ) -> Dict[str, Any]:
        try:

            # 사용자 메시지 의도 분류
            intent = self._classify(prompt)

            # 의도에 따른 다음 노드 결정
            next_node = INTENT_TO_NODE_MAP.get(intent, "conversation")

            # 상태 생성
            state: PromptRouterState = {
                "user_input": prompt,
                "intent": intent.value,
                "next_node": next_node,
                "messages": [{"role": "user", "content": prompt}],
                "context": {"intent": intent.value},
            }

            return {
                "response": f"의도 분류: {intent.value}",
                "state": state,
                "intent": intent.value,
                "next_node": next_node,
            }
        except Exception as e:
            import traceback

            traceback.print_exc()
            return {
                "response": f"[의도 분류 오류] {str(e)}",
                "intent": Intent.UNKNOWN.value,
                "next_node": "conversation",
            }

    def _classify(self, message: str) -> Intent:
        response = self.chain.invoke({"message": message}).content.strip().lower()
        intent = json.loads(response)["intent"]
        try:
            return (
                Intent(intent)
                if intent in [e.value for e in Intent]
                else Intent.UNKNOWN
            )
        except ValueError:
            return Intent.UNKNOWN
