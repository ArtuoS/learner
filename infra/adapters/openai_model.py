from collections.abc import AsyncGenerator

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

from infra.ports.model import Model
from infra.adapters.tools import ingest_document
from services.knowledge import KnowledgeService

from typing import AsyncGenerator
from langchain_core.messages import AIMessageChunk, HumanMessage, ToolMessage, SystemMessage


class OpenAIModel(Model):
    _client: ChatOpenAI
    # _client_with_tools: ChatOpenAI
    knowledge_service: KnowledgeService
    
    def __init__(self, knowledge_service: KnowledgeService) -> None:
        self.knowledge_service = knowledge_service
        self._client = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL_NAME", "gpt-5-nano"),
            temperature=0,
            timeout=60,
            max_tokens=4096,
        )
        
        # self._client_with_tools = self._client.bind_tools([ingest_document])

    def ask(self, instructions: str, context: str, question: str) -> str:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", instructions),
            ("human", "Context: {context}\nQuestion: {question}")
        ])

        chain = prompt_template | self._client
        response = chain.invoke({"context": context, "question": question})

        if response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call["name"] == "ingest_document_tool":
                    tool_output = ingest_document.invoke({
                        **tool_call["args"],
                        "service": self.knowledge_service
                    })
                    print(f"Resultado da execução da ferramenta: {tool_output}")
        
        return str(response.content)

    async def ask_stream(self, instructions: str, context: str, question: str) -> AsyncGenerator[str, None]:
        messages = [
            SystemMessage(content=instructions),
            HumanMessage(content=f"Context: {context}\nQuestion: {question}")
        ]

        # Usamos self._client_with_tools para permitir que ele decida chamar ferramentas
        # Nota: Usamos o astream_events ou acumulamos manualmente os chunks
        final_chunk: AIMessageChunk | None = None

        # Primeiro Stream: O modelo avalia a pergunta e decide se chama a ferramenta ou responde direto
        async for chunk in self._client.astream(messages):
            if final_chunk is None:
                final_chunk = chunk
            else:
                final_chunk += chunk
            
            # Se for texto direto (sem ferramentas), já vai entregando ao usuário
            if chunk.content and not final_chunk.tool_calls:
                yield chunk.content

        # 2. Se o modelo decidiu que precisa chamar a ferramenta
        if final_chunk and final_chunk.tool_calls:
            # Adiciona a resposta de intenção do modelo ao histórico de mensagens
            messages.append(final_chunk)
            
            # for tool_call in final_chunk.tool_calls:
            #     if tool_call["name"] == "ingest_document_tool":
            #         # Executa a ferramenta de forma assíncrona (ou síncrona se não tiver ainvoke)
            #         # Nota: Certifique-se de usar 'ainvoke' se sua ferramenta/serviço for assíncrona,
            #         # ou use run_in_executor para não bloquear a thread do event loop.
            #         tool_output = await ingest_document.invoke({
            #             **tool_call["args"],
            #             "service": self.knowledge_service
            #         })
                    
            #         # Registra o resultado da ferramenta no histórico de mensagens
            #         messages.append(
            #             ToolMessage(
            #                 content=str(tool_output),
            #                 tool_call_id=tool_call["id"]
            #             )
            #         )

            # Segundo Stream: Com a resposta da ferramenta no histórico,
            # geramos a resposta final em texto para o usuário
            async for chunk in self._client.astream(messages):
                if chunk.content:
                    yield chunk.content
