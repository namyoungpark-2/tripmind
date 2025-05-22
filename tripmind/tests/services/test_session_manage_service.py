import unittest
from unittest.mock import patch, MagicMock

from tripmind.services.session_manage_service import SessionManageService
from tripmind.models.session import ConversationSession


class TestSessionManageService(unittest.TestCase):
    """세션 관리 서비스 테스트"""

    def setUp(self):
        # ConversationSession.objects.get_or_create 모킹
        self.get_or_create_patch = patch(
            "tripmind.models.session.ConversationSession.objects.get_or_create"
        )
        self.mock_get_or_create = self.get_or_create_patch.start()

        # 모의 세션 객체 생성
        self.mock_session = MagicMock(spec=ConversationSession)
        self.mock_session.session_id = "test_session"

        # get_or_create가 (session, created) 튜플 반환하도록 설정
        self.mock_get_or_create.return_value = (self.mock_session, False)

        # ConversationBufferMemory 패치
        self.memory_patch = patch(
            "tripmind.services.session_manage_service.ConversationBufferMemory"
        )
        self.mock_memory_class = self.memory_patch.start()
        self.mock_memory = MagicMock()
        self.mock_memory_class.return_value = self.mock_memory

        # 서비스 초기화
        self.service = SessionManageService()

    def tearDown(self):
        # 패치 종료
        self.get_or_create_patch.stop()
        self.memory_patch.stop()

    def test_get_or_create_session(self):
        """세션 가져오기 또는 생성 테스트"""
        # 서비스 호출
        session = self.service.get_or_create_session("test_session")

        # 메서드 호출 검증
        self.mock_get_or_create.assert_called_once_with(session_id="test_session")

        # 결과 검증
        self.assertEqual(session, self.mock_session)

    def test_get_session_memory_new(self):
        """새 세션 메모리 가져오기 테스트"""
        # 서비스 호출
        memory = self.service.get_session_memory("new_session")

        # 메모리 생성 검증
        self.mock_memory_class.assert_called_once_with(
            memory_key="chat_history", return_messages=True
        )

        # 결과 검증
        self.assertEqual(memory, self.mock_memory)
        self.assertIn("new_session", self.service.memories)

    def test_get_session_memory_existing(self):
        """기존 세션 메모리 가져오기 테스트"""
        # 메모리 캐시에 세션 추가
        existing_memory = MagicMock()
        self.service.memories["existing_session"] = existing_memory

        # 서비스 호출
        memory = self.service.get_session_memory("existing_session")

        # 메모리 생성 호출 안 됨 검증
        self.mock_memory_class.assert_not_called()

        # 결과 검증
        self.assertEqual(memory, existing_memory)

    def test_clear_memory_existing(self):
        """기존 세션 메모리 삭제 테스트"""
        # 메모리 캐시에 세션 추가
        self.service.memories["session_to_clear"] = MagicMock()

        # 서비스 호출
        result = self.service.clear_memory("session_to_clear")

        # 결과 검증
        self.assertTrue(result)
        self.assertNotIn("session_to_clear", self.service.memories)

    def test_clear_memory_nonexistent(self):
        """존재하지 않는 세션 메모리 삭제 테스트"""
        # 서비스 호출
        result = self.service.clear_memory("nonexistent_session")

        # 결과 검증
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
