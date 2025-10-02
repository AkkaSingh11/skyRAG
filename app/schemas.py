from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class PersonInfo(BaseModel):
    """Information about a person"""
    name: str = Field(description="Full name of the person")
    age: Optional[int] = Field(description="Age of the person")
    occupation: str = Field(description="Person's job or profession")
    skills: List[str] = Field(description="List of skills or expertise")

class RouteDecision(BaseModel):
    route: Literal["rag", "answer", "end"]
    reply: str | None = Field(None, description="Filled only when route == 'end'")

class RagJudge(BaseModel):
    sufficient: bool
