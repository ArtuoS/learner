from dotenv import load_dotenv
from infra.database import Database
from infra.llm.adapters.langchain_splitter import LangChainSplitter
from infra.llm.adapters.openai_model import OpenAIModel
from service.ask import Ask
from service.knowledge import Knowledge


def main():
    load_dotenv()
    db = Database()
    model = OpenAIModel()
    splitter = LangChainSplitter()
    knowledge = Knowledge(db, splitter)
    ask = Ask(model)
    knowledge.fetch_and_apply([
        "https://raw.githubusercontent.com/gastonstat/StarWars/refs/heads/master/Text_files/EpisodeIV_dialogues.txt"
    ])

    question = "Is Luke Skywalker a Jedi?"
    results = knowledge.query(question)

    context = "\n\n".join(results)
    if len(context) > 3000:
        context = context[:3000] + "..."
        
    print(f"Context: {context}")

    print(ask.get_response(f"""
            You are only allowed to answer questions about the context provided. If the question is not related to the context, respond with "I don't know.".
        """, context, question))


if __name__ == "__main__":
    main()
