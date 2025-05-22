from typing import Dict, Any


class BaseAgentExcutor:
    def __init__(self):
        pass

    def process_prompt(
        self, prompt: str, session_id: str = "default"
    ) -> Dict[str, Any]:
        pass
