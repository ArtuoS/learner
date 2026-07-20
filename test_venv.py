import sys
import openai
import langchain_core
import chromadb
import fastapi

print("executable:", sys.executable)
print("version:", sys.version)
print("openai:", openai.__version__)
print("langchain_text_splitters: OK")
print("langchain_core:", langchain_core.__version__)
print("chromadb:", chromadb.__version__)
print("fastapi:", fastapi.__version__)
