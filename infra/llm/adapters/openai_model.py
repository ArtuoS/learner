from openai import OpenAI
import os

from infra.llm.ports.model import Model


class OpenAIModel(Model):
    _client: OpenAI

    def __init__(self):
        self._client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    def ask(self, instructions: str, context: str, question: str) -> list[str]:
        self._client.responses.create(
            model=os.getenv("OPENAI_MODEL_NAME", "gpt-5-nano"),
            instructions=instructions,
            input=self._format_input(context, question),
        ).output_text
        pass
        
    @staticmethod
    def _format_input(context: str, question: str) -> str:
        return f"""
            Context: {context}
            Question: {question}
        """
