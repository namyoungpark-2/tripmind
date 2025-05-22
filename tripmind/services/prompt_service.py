from typing import Dict


class PromptService:
    def build_prompt(self, request: Dict) -> str:
        """프롬프트 구성"""
        destination = request.get("destination", "")
        duration = request.get("duration", "")
        travelers = request.get("travelers", "")
        budget = request.get("budget", "")
        preferences = request.get("preferences", "")
        special_requirements = request.get("special_requirements", "")

        prompt = f"""
          {destination}으로 {duration} 동안의 여행 일정을 작성해 주세요.
          [여행 기본 정보]
          - 여행지: {destination}
          - 여행 기간: {duration}
          - 여행자 수: {travelers}
          - 예산: {budget}
        """

        if preferences:
            prompt += f"\n[선호 사항]\n{preferences}"

        if special_requirements:
            prompt += f"\n[특별 요구사항]\n{special_requirements}"

        return prompt.strip()
