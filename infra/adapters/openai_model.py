from collections.abc import AsyncGenerator

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

from infra.ports.model import Model


class OpenAIModel(Model):
    _client: ChatOpenAI

    def __init__(self):
        self._client = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL_NAME", "gpt-5-nano"),
            temperature=0,
            timeout=60,
            max_tokens=4096,
        )

    def ask(self, instructions: str, context: str, question: str) -> str:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", instructions),
            ("human", "Context: {context}\nQuestion: {question}")
        ])

        chain = prompt_template | self._client
        response = chain.invoke({"context": context, "question": question})

        return str(response.content)

    async def ask_stream(self, instructions: str, context: str, question: str) -> AsyncGenerator[str, None]:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", instructions),
            ("human", "Context: {context}\nQuestion: {question}")
        ])

        chain = prompt_template | self._client

        async for chunk in chain.astream({"context": context, "question": question}):
            if chunk.content:
                yield chunk.content
