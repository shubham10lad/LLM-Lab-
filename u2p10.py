
from pathlib import Path

from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama


Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

Settings.llm = Ollama(
    model="llama3.2",
    request_timeout=120.0,
)

DATA_DIR = Path(__file__).parent / "data"   

if not DATA_DIR.exists():
    raise FileNotFoundError(
        f"Data directory not found: {DATA_DIR}"
    )


documents = SimpleDirectoryReader(
    input_dir=str(DATA_DIR),
    required_exts=[".txt", ".md"],
).load_data()

if not documents:
    raise ValueError(
        "No .txt or .md files found in the data directory."
    )

print(f"Loaded {len(documents)} documents.")

print("Creating VectorStoreIndex...")
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine(
    similarity_top_k=3
)

print("GEMINI MODELS PRICING Q&A SYSTEM")
print("-----------------------------------")
print("Ask questions about Gemini models,")
print("pricing, and features.")
print("Type 'exit' to stop.\n")

while True:
    question = input("Enter your question: ").strip()

    if question.lower() in ["exit", "quit"]:
        print("Thank you for using the system!")
        break

    if not question:
        print("Please enter a question.\n")
        continue

    try:
        response = query_engine.query(question)
        print("\nAnswer:")
        print(response)
        print("\n" + "-" * 50 + "\n")

    except Exception as error:
        print(f"Error while answering: {error}")
