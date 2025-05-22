import unittest
from unittest.mock import patch, mock_open

from tripmind.llm.prompt_loader import PromptLoader


class TestPromptLoader(unittest.TestCase):
    """프롬프트 로더 테스트"""

    def setUp(self):
        # YAML 파일의 open 함수를 패치
        self.open_patch = patch("builtins.open", new_callable=mock_open)
        self.mock_open = self.open_patch.start()

        # yaml.safe_load 패치
        self.yaml_patch = patch("yaml.safe_load")
        self.mock_yaml_load = self.yaml_patch.start()

        # 로더 초기화
        self.loader = PromptLoader()

    def tearDown(self):
        # 패치 종료
        self.open_patch.stop()
        self.yaml_patch.stop()

    def test_load_prompt_template_from_yaml(self):
        """YAML 파일에서 프롬프트 템플릿 로드 테스트"""
        # YAML 로더가 반환할 데이터 설정
        yaml_data = {
            "id": "test-prompt",
            "description": "테스트 프롬프트",
            "template": "이것은 {variable}을 포함한 테스트 프롬프트입니다.",
        }
        self.mock_yaml_load.return_value = yaml_data

        # 로더 실행
        template = self.loader.load_prompt_template_from_yaml("itinerary/v1.yaml")

        # 파일 열기 확인
        self.mock_open.assert_called_once()

        # yaml.safe_load 호출 확인
        self.mock_yaml_load.assert_called_once()

        # 결과 검증
        self.assertEqual(template, "이것은 {variable}을 포함한 테스트 프롬프트입니다.")

    def test_load_prompt_template_from_yaml_with_format(self):
        """템플릿에 format 적용 테스트"""
        # YAML 로더가 반환할 데이터 설정
        yaml_data = {
            "id": "test-prompt",
            "description": "테스트 프롬프트",
            "template": "이것은 {variable}을 포함한 테스트 프롬프트입니다.",
        }
        self.mock_yaml_load.return_value = yaml_data

        # 로더 실행
        template = self.loader.load_prompt_template_from_yaml("itinerary/v1.yaml")

        # 템플릿에 format 적용
        formatted = template.format(variable="값")

        # 결과 검증
        self.assertEqual(formatted, "이것은 값을 포함한 테스트 프롬프트입니다.")


if __name__ == "__main__":
    unittest.main()
