
from typing import List, Optional, Union, Tuple
from pydantic import BaseModel, Field


class Messages(BaseModel):
    role: str = Field(..., description="Role of the message sender, either 'user' or 'assistant'")
    content: str = Field(..., description="Content of the message")


class FeedBack(BaseModel):
    score: float = Field(..., description="Feedback score ranging from 0 to 1")
    comment: str = Field(..., description="Feedback comment")


class RevisedResponse(BaseModel):
    revised: str = Field(..., description="Revised response content")


class Trajectory(BaseModel):
    messages: List[Tuple[List[Messages], Optional[Union[FeedBack, RevisedResponse, None]]]] = Field(..., description="A list of conversation turns, each as (messages, feedback/revised/None)")
