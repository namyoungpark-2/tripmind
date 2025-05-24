from pydantic import BaseModel


class FinalResponseInput(BaseModel):
    response: str
