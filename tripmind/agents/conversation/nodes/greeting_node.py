from typing import Dict, Any
from pathlib import Path
import logging

from tripmind.services.prompt.prompt_service import prompt_service


PROMPT_DIR = Path(__file__).parent / "../prompt_templates"

logger = logging.getLogger(__name__)


def greeting_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """인사 노드"""
    greeting_msg = prompt_service.get_string_prompt(PROMPT_DIR / "greeting" / "v1.yaml")
    state["messages"].append({"role": "assistant", "content": greeting_msg})

    return state
