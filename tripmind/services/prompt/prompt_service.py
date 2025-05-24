import yaml
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)


class PromptService:
    def get_system_prompt(self, template_path: str) -> ChatPromptTemplate:
        prompt_template = self._load_prompt_template_from_yaml(template_path)
        system_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt_template),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        return system_prompt

    def get_prompt_template(self, template_path: str, partial_variables: dict) -> str:
        prompt_template = self._load_prompt_template_from_yaml(template_path)
        return PromptTemplate.from_template(
            template=prompt_template,
            partial_variables=partial_variables,
        )

    def get_prompt_templatet(
        self, template_path: str, partial_variables: dict
    ) -> ChatPromptTemplate:
        prompt_template = self._load_prompt_template_from_yaml(template_path)
        return ChatPromptTemplate.from_template(
            template=prompt_template,
            partial_variables=partial_variables,
        )

    def get_string_prompt(self, template_path: str) -> str:
        prompt_template = self._load_prompt_template_from_yaml(template_path)
        return prompt_template

    def _load_prompt_template_from_yaml(self, template_path: str) -> str:
        """YAML 파일을 읽어서 프롬프트 템플릿을 문자열로 반환"""

        with open(template_path, "r", encoding="utf-8") as f:
            template_data = yaml.safe_load(f)
            prompt_str = template_data["template"]
            return prompt_str


# 싱글톤 패턴 적용
prompt_service = PromptService()
