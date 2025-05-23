import unittest
from unittest.mock import patch, MagicMock

from tripmind.agents.prompt_router.prompt_router_agent_executor import (
    PromptRouterAgentExecutor,
)
from tripmind.agents.prompt_router.constants.intent_constants import Intent


class TestPromptRouterAgent(unittest.TestCase):
    """프롬프트 라우터 에이전트 테스트"""

    def setUp(self):
        # LLM과 프롬프트 로더를 모킹하기 위한 패치 설정
        self.prompt_loader_patch = patch(
            "tripmind.llm.prompt_loader.prompt_loader.load_prompt_template_from_yaml"
        )
        self.mock_prompt_loader = self.prompt_loader_patch.start()
        self.mock_prompt_loader.return_value = "사용자의 메시지를 분석하여 다음 중 하나의 목적을 선택하세요: {intent_descriptions}\n메시지: {message}\n의도:"

        # LLM 결과 모킹
        self.llm_patch = patch(
            "tripmind.agents.prompt_router.prompt_router_agent_llm.prompt_router_agent_llm.get_llm"
        )
        self.mock_llm_getter = self.llm_patch.start()
        self.mock_llm = MagicMock()
        self.mock_llm.model = "test-model"
        self.mock_llm_getter.return_value = self.mock_llm

        # _classify 메서드를 따로 모킹
        self.classify_patch = patch.object(PromptRouterAgentExecutor, "_classify")
        self.mock_classify = self.classify_patch.start()

        # 에이전트 초기화
        self.agent = PromptRouterAgentExecutor()

    def tearDown(self):
        # 패치 종료
        self.prompt_loader_patch.stop()
        self.llm_patch.stop()
        self.classify_patch.stop()

    def test_process_prompt_itinerary_intent(self):
        """여행 일정 의도 분류 테스트"""
        # _classify 메서드가 ITINERARY 의도를 반환하도록 설정
        self.mock_classify.return_value = Intent.ITINERARY

        # 에이전트 실행
        result = self.agent.process_prompt("서울로 3박 4일 여행 계획 짜줘")

        # 결과 검증
        self.assertEqual(result["intent"], "itinerary")
        self.assertEqual(result["next_node"], "itinerary")
        self.assertIn("state", result)
        self.assertEqual(result["state"]["intent"], "itinerary")

    def test_process_prompt_conversation_intent(self):
        """일반 대화 의도 분류 테스트"""
        # _classify 메서드가 CONVERSATION 의도를 반환하도록 설정
        self.mock_classify.return_value = Intent.CONVERSATION

        # 에이전트 실행
        result = self.agent.process_prompt("오늘 날씨 어때?")

        # 결과 검증
        self.assertEqual(result["intent"], "conversation")
        self.assertEqual(result["next_node"], "conversation")
        self.assertIn("state", result)
        self.assertEqual(result["state"]["intent"], "conversation")

    def test_process_prompt_greeting_intent(self):
        """인사 의도 분류 테스트"""
        # _classify 메서드가 GREETING 의도를 반환하도록 설정
        self.mock_classify.return_value = Intent.GREETING

        # 에이전트 실행
        result = self.agent.process_prompt("안녕하세요")

        # 결과 검증
        self.assertEqual(result["intent"], "greeting")
        # 현재 INTENT_TO_NODE_MAP에 GREETING 매핑이 없으므로 기본값인 conversation으로 설정됨
        self.assertEqual(result["next_node"], "conversation")
        self.assertIn("state", result)
        self.assertEqual(result["state"]["intent"], "greeting")

    def test_process_prompt_exception(self):
        """예외 처리 테스트"""
        # _classify 메서드가 예외를 발생시키도록 설정
        self.mock_classify.side_effect = Exception("테스트 예외")

        # 에이전트 실행
        result = self.agent.process_prompt("예외 발생 테스트")

        # 결과 검증
        self.assertEqual(result["intent"], "unknown")
        self.assertEqual(result["next_node"], "conversation")
        self.assertIn("[의도 분류 오류]", result["response"])


if __name__ == "__main__":
    unittest.main()
