# llm/prompt_loader.py

import yaml
from pathlib import Path
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)

PROMPT_DIR = Path(__file__).parent / "prompt_templates"


class PromptLoader:
    def get_system_prompt(self, template_path: str) -> str:
        prompt_template = self._load_prompt_template_from_yaml(template_path)
        system_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt_template),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        return system_prompt

    def get_prompt_template(self, template_path: str, partial_variables: dict) -> str:
        prompt_template = self._load_prompt_template_from_yaml(template_path)
        PromptTemplate.from_template(
            template=prompt_template,
            partial_variables=partial_variables,
        )

    def _load_prompt_template_from_yaml(self, template_path: str) -> str:
        """YAML 파일을 읽어서 프롬프트 템플릿을 문자열로 반환"""
        full_path = PROMPT_DIR / template_path
        with open(full_path, "r", encoding="utf-8") as f:
            template_data = yaml.safe_load(f)
            prompt_str = template_data["template"]
            return prompt_str


# 싱글톤 패턴 적용
prompt_loader = PromptLoader()
