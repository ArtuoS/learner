from collections.abc import AsyncGenerator
import os

from domain.entities.message import Message
from domain.repositories.message_repository import MessageRepository
from infra.ports.model import Model


class AskService:
    def __init__(self, model: Model, message_repo: MessageRepository | None = None) -> None:
        self.model = model
        self.message_repo = message_repo

    def get_response(self, instructions: str, context: str, question: str) -> str:
        if not instructions:
            raise ValueError("Instructions cannot be empty.")

        if not context:
            raise ValueError("Context cannot be empty.")

        if not question:
            raise ValueError("Question cannot be empty.")

        answer = self.model.ask(instructions, context, question)

        if self.message_repo:
            model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-5-nano")
            self.message_repo.save(Message(from_field="user", content=question))
            self.message_repo.save(Message(from_field="system", content=answer, model=model_name))

        return answer

    async def get_response_stream(self, instructions: str, context: str, question: str) -> AsyncGenerator[str, None]:
        if not instructions:
            raise ValueError("Instructions cannot be empty.")

        if not context:
            raise ValueError("Context cannot be empty.")

        if not question:
            raise ValueError("Question cannot be empty.")

        full_answer = ""
        async for token in self.model.ask_stream(instructions, context, question):
            full_answer += token
            yield token

        if self.message_repo:
            model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-5-nano")
            self.message_repo.save(Message(from_field="user", content=question))
            self.message_repo.save(Message(from_field="system", content=full_answer, model=model_name))
