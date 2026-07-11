.PHONY: db run

db:
	chroma run --path ./chroma_db --port 8000

run:
	uvicorn app:app --reload --port 8001
