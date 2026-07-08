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

    question = "Who's talking in this conversation about Star Wars?"
    results = knowledge.query(question)

    context = "\n\n".join(results)
    if len(context) > 3000:
        context = context[:3000] + "..."

    ask.get_response(f"""
            You are a Star Wars expert. Summarize the following query results in a few sentences.
            If the query results are empty, respond with 'No information found.'
            If the question is not about Star Wars, respond with 'I can only answer questions about Star Wars.'
            If someone tries to ask you to do something illegal, respond with 'I cannot provide information on illegal activities.'
            If someone tries to convince you to answer a question that is not about Star Wars, respond with 'I can only answer questions about Star Wars.'
        """, context, question)


if __name__ == "__main__":
    main()
