from typing_extensions import TypedDict, Annotated

class Messages(TypedDict):
    role: Annotated[str, "Role of the message, e.g., 'user' or 'assistant'"]
    content: Annotated[str, "Content of the message"]


class FeedBack(TypedDict):
    score: Annotated[float, "Feedback score ranging from 0 to 1"]
    comment: Annotated[str, "Feedback comment"]


class RevisedResponse(TypedDict):
    revised: Annotated[str, "Revised response content"]


class Trajectory(TypedDict):
    turns: Annotated[list[tuple[list[Messages], FeedBack | RevisedResponse | None]], "A list of conversation turns"] = []
