from infra.llm.ports.model import Model


class AskService:
    def __init__(self, model: Model) -> None:
        self.model = model
        pass

    def get_response(self, instructions: str, context: str, question: str) -> str:
        if not instructions:
            raise ValueError("Instructions cannot be empty.")
        
        if not context:
            raise ValueError("Context cannot be empty.")
        
        if not question:
            raise ValueError("Question cannot be empty.")
        
        return self.model.ask(instructions, context, question)
