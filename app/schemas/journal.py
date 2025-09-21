from pydantic import BaseModel
from typing import List

class JournalRequest(BaseModel):
    entry: str

class JournalResponse(BaseModel):
    suggestions: List[str]    