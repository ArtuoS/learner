import sys
print("executable:", sys.executable)
print("version:", sys.version)

import openai
print("openai:", openai.__version__)

print("langchain_text_splitters: OK")

import langchain_core
print("langchain_core:", langchain_core.__version__)

import chromadb
print("chromadb:", chromadb.__version__)

import fastapi
print("fastapi:", fastapi.__version__)
