
from langmem import create_prompt_optimizer
from models import Trajectory
from langchain_google_genai import ChatGoogleGenerativeAI


class PromptOptimizer:
    def __init__(self, trajectories=[]):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
        )
        self.trajectories: list[Trajectory] = trajectories
        self.optimizer = create_prompt_optimizer(
            self.llm,
            kind="metaprompt",
            config={"max_reflection_steps": 1, "min_reflection_steps": 0},
        )

    def optimize(self, prompt: str):
        updated = self.optimizer.invoke({"trajectories": self.trajectories, "prompt": prompt})
        return updated
