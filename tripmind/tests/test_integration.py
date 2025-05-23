import unittest
from unittest.mock import patch

from tripmind.agents.prompt_router.prompt_router_agent_executor import (
    PromptRouterAgentExecutor,
)
from tripmind.agents.itinerary.itinerary_agent_executor import ItineraryAgentExecutor
from tripmind.agents.prompt_router.constants.intent_constants import Intent


class TestIntegration(unittest.TestCase):
    """에이전트 통합 테스트"""

    def setUp(self):
        # 프롬프트 라우터 에이전트의 _classify 메서드 패치
        self.router_classify_patch = patch.object(
            PromptRouterAgentExecutor, "_classify"
        )
        self.mock_router_classify = self.router_classify_patch.start()

        # 여행 일정 에이전트의 process_prompt 메서드 패치
        self.itinerary_process_patch = patch.object(
            ItineraryAgentExecutor, "process_prompt"
        )
        self.mock_itinerary_process = self.itinerary_process_patch.start()

        # 에이전트 초기화
        self.router_agent = PromptRouterAgentExecutor()
        self.itinerary_agent = ItineraryAgentExecutor()

    def tearDown(self):
        # 패치 종료
        self.router_classify_patch.stop()
        self.itinerary_process_patch.stop()

    def test_router_to_itinerary_flow(self):
        """라우터 에이전트에서 여행 일정 에이전트로의 흐름 테스트"""
        # 라우터 에이전트가 ITINERARY 의도를 반환하도록 설정
        self.mock_router_classify.return_value = Intent.ITINERARY

        # 여행 일정 에이전트가 반환할 응답 설정
        itinerary_response = {
            "response": "서울 여행 계획을 만들어 드릴게요.",
            "messages": [
                {"role": "user", "content": "서울로 3박 4일 여행 계획 짜줘"},
                {"role": "assistant", "content": "서울 여행 계획을 만들어 드릴게요."},
            ],
            "context": {"destination": "서울", "duration": "3박 4일"},
        }
        self.mock_itinerary_process.return_value = itinerary_response

        # 테스트 시나리오:
        # 1. 사용자가 여행 계획 요청
        user_input = "서울로 3박 4일 여행 계획 짜줘"

        # 2. 라우터 에이전트가 의도 분류
        router_result = self.router_agent.process_prompt(user_input, "test_session")

        # 3. 의도에 따라 적절한 에이전트 선택 및 처리
        next_node = router_result["next_node"]
        self.assertEqual(next_node, "itinerary")

        if next_node == "itinerary":
            result = self.itinerary_agent.process_prompt(user_input, "test_session")
        else:
            self.fail("의도가 itinerary가 아님")

        # 결과 검증
        self.mock_itinerary_process.assert_called_once_with(
            user_input, "test_session", "ask_info_node"
        )
        self.assertEqual(result["response"], "서울 여행 계획을 만들어 드릴게요.")
        self.assertEqual(result["context"]["destination"], "서울")

    def test_session_continuity(self):
        """세션 연속성 테스트"""
        # 첫 번째 여행 일정 에이전트 응답 설정
        first_response = {
            "response": "어디로 여행을 가실 계획인가요?",
            "messages": [
                {"role": "user", "content": "여행 계획 세워줘"},
                {"role": "assistant", "content": "어디로 여행을 가실 계획인가요?"},
            ],
            "context": {"intent": "itinerary"},
        }

        # 두 번째 여행 일정 에이전트 응답 설정
        second_response = {
            "response": "서울 여행 계획을 만들어 드릴게요.",
            "messages": [
                {"role": "user", "content": "여행 계획 세워줘"},
                {"role": "assistant", "content": "어디로 여행을 가실 계획인가요?"},
                {"role": "user", "content": "서울로 가고 싶어요"},
                {"role": "assistant", "content": "서울 여행 계획을 만들어 드릴게요."},
            ],
            "context": {"destination": "서울", "intent": "itinerary"},
        }

        # 라우터 에이전트가 항상 ITINERARY 의도를 반환하도록 설정
        self.mock_router_classify.return_value = Intent.ITINERARY

        # 여행 일정 에이전트 응답 설정 (두 번 호출될 예정)
        self.mock_itinerary_process.side_effect = [first_response, second_response]

        # 테스트 시나리오:
        # 1. 첫 번째 사용자 입력
        first_result = self.router_agent.process_prompt(
            "여행 계획 세워줘", "test_session"
        )
        self.assertEqual(first_result["next_node"], "itinerary")

        first_itinerary_result = self.itinerary_agent.process_prompt(
            "여행 계획 세워줘", "test_session"
        )
        self.assertEqual(
            first_itinerary_result["response"], "어디로 여행을 가실 계획인가요?"
        )

        # 2. 두 번째 사용자 입력 (같은 세션)
        second_result = self.router_agent.process_prompt(
            "서울로 가고 싶어요", "test_session"
        )
        self.assertEqual(second_result["next_node"], "itinerary")

        second_itinerary_result = self.itinerary_agent.process_prompt(
            "서울로 가고 싶어요", "test_session"
        )
        self.assertEqual(
            second_itinerary_result["response"], "서울 여행 계획을 만들어 드릴게요."
        )
        self.assertEqual(second_itinerary_result["context"]["destination"], "서울")

        # 세션 연속성 확인 (두 번째 응답에 첫 번째 대화 내용 포함)
        self.assertEqual(len(second_itinerary_result["messages"]), 4)


if __name__ == "__main__":
    unittest.main()
