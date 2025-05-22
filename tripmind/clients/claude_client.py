import os
import anthropic
from .base_llm_client import BaseLLMClient


class ClaudeClient(BaseLLMClient):
    """
    Claude API 클라이언트
    """

    def __init__(self):
        """
        API 키와 모델 정보 초기화
        """
        print("환경 변수 로딩중...")
        api_key_value = os.getenv("ANTHROPIC_API_KEY")
        print(f"ANTHROPIC_API_KEY: {'설정됨' if api_key_value else '설정되지 않음'}")
        if api_key_value:
            print(f"API 키 길이: {len(api_key_value)}")
            print(f"API 키 마지막 문자: {api_key_value[-1]}")

        self.api_key = api_key_value
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일에 API 키를 추가하거나 환경 변수로 설정해주세요."
            )

        # 클라이언트 생성 시도
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            print("Anthropic 클라이언트가 성공적으로 생성되었습니다.")
        except Exception as e:
            print(f"Anthropic 클라이언트 생성 오류: {str(e)}")
            raise

        self.model = "claude-3-opus-20240229"

    def generate_text(self, prompt: str) -> str:
        """
        텍스트 생성 요청

        Args:
            prompt: 사용자 프롬프트

        Returns:
            생성된 텍스트
        """
        try:
            print("텍스트 생성 요청 시작...")
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )
            print("텍스트 생성 요청 성공")
            return message.content[0].text
        except Exception as e:
            error_message = f"오류가 발생했습니다: {str(e)}"
            print(error_message)
            return error_message
