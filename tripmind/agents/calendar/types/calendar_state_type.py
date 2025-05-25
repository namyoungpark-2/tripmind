from typing import Optional

from tripmind.agents.common.types.base_state_type import BaseState


class CalendarState(BaseState):
    response: Optional[str]
