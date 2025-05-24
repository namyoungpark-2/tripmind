from typing import Optional

from tripmind.agents.common.types.base_state_type import BaseState


class SharingRouterState(BaseState):
    response: Optional[str]
