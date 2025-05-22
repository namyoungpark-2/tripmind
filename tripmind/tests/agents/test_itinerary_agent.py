import unittest
from unittest.mock import patch

from tripmind.agents.itinerary.itinerary_agent_executor import ItineraryAgentExecutor
from tripmind.agents.itinerary.itinerary_agent_graph import itinerary_graph


class TestItineraryAgent(unittest.TestCase):
    """여행 일정 에이전트 테스트"""

    def setUp(self):
        # 그래프 invoke 메서드 모킹
        self.graph_patch = patch.object(itinerary_graph, "invoke")
        self.mock_graph_invoke = self.graph_patch.start()

        # 그래프 get_state 메서드 모킹
        self.get_state_patch = patch.object(itinerary_graph, "get_state")
        self.mock_get_state = self.get_state_patch.start()

        # 에이전트 초기화
        self.agent = ItineraryAgentExecutor()

    def tearDown(self):
        # 패치 종료
        self.graph_patch.stop()
        self.get_state_patch.stop()

    def test_process_prompt_new_session(self):
        """새 세션에서의 프롬프트 처리 테스트"""
        # get_state가 None을 반환하도록 설정 (새 세션)
        self.mock_get_state.return_value = None

        # invoke가 반환할 결과 설정
        mock_result = {
            "response": "여행 계획을 만들어 드릴게요.",
            "messages": [
                {"role": "user", "content": "서울로 3박 4일 여행 계획 짜줘"},
                {"role": "assistant", "content": "여행 계획을 만들어 드릴게요."},
            ],
            "context": {"destination": "서울", "duration": "3박 4일"},
        }
        self.mock_graph_invoke.return_value = mock_result

        # 에이전트 실행
        result = self.agent.process_prompt(
            "서울로 3박 4일 여행 계획 짜줘", "test_session_1"
        )

        # 그래프 호출 검증
        self.mock_graph_invoke.assert_called_once()
        # 첫 번째 인자 확인 (state)
        state_arg = self.mock_graph_invoke.call_args[0][0]
        self.assertEqual(state_arg["user_input"], "서울로 3박 4일 여행 계획 짜줘")
        self.assertEqual(state_arg["next_node"], "ask_info_node")  # 기본 시작 노드

        # 결과 검증
        self.assertEqual(result["response"], "여행 계획을 만들어 드릴게요.")
        self.assertEqual(len(result["messages"]), 2)
        self.assertEqual(result["context"]["destination"], "서울")

    def test_process_prompt_existing_session(self):
        """기존 세션에서의 프롬프트 처리 테스트"""
        # get_state가 기존 세션 상태를 반환하도록 설정
        existing_state = {
            "messages": [
                {"role": "user", "content": "여행 계획 짜줘"},
                {"role": "assistant", "content": "어디로 여행을 가실 계획인가요?"},
            ],
            "context": {"intent": "itinerary"},
        }
        self.mock_get_state.return_value = existing_state

        # invoke가 반환할 결과 설정
        mock_result = {
            "response": "서울 여행 계획을 만들어 드릴게요.",
            "messages": [
                {"role": "user", "content": "여행 계획 짜줘"},
                {"role": "assistant", "content": "어디로 여행을 가실 계획인가요?"},
                {"role": "user", "content": "서울로 가고 싶어요"},
                {"role": "assistant", "content": "서울 여행 계획을 만들어 드릴게요."},
            ],
            "context": {"destination": "서울", "intent": "itinerary"},
        }
        self.mock_graph_invoke.return_value = mock_result

        # 에이전트 실행
        result = self.agent.process_prompt("서울로 가고 싶어요", "test_session_2")

        # 그래프 호출 검증
        self.mock_graph_invoke.assert_called_once()

        # 결과 검증
        self.assertEqual(result["response"], "서울 여행 계획을 만들어 드릴게요.")
        self.assertEqual(len(result["messages"]), 4)
        self.assertEqual(result["context"]["destination"], "서울")

    def test_process_prompt_exception(self):
        """예외 처리 테스트"""
        # invoke가 예외를 발생시키도록 설정
        self.mock_graph_invoke.side_effect = Exception("테스트 예외")

        # 에이전트 실행
        result = self.agent.process_prompt(
            "서울로 3박 4일 여행 계획 짜줘", "test_session_3"
        )

        # 결과 검증
        self.assertIn("[여행 일정 생성 오류]", result["response"])
        self.assertEqual(len(result["messages"]), 0)
        self.assertEqual(result["context"], {})


if __name__ == "__main__":
    unittest.main()
