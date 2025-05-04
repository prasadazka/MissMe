import os
import json
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

# === CONFIG ===
VECTOR_DB_DIR = "rag_vector_db"
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # lightweight and fast

# === Load RAG documents for specific character ===
def load_rag_documents(character_id):
    docs = []
    accepted_file = f"accepted_{character_id}.json"
    personality_file = f"personality_{character_id}.json"

    if os.path.exists(accepted_file):
        with open(accepted_file, "r", encoding="utf-8") as f:
            items = json.load(f)
            for entry in items:
                content = f"Q: {entry['question']}\nA: {entry['response']}"
                docs.append(Document(page_content=content, metadata={"source": accepted_file}))

    if os.path.exists(personality_file):
        with open(personality_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for qa in data.get("personality_answers", []):
                content = f"Q: {qa['question']}\nA: {qa['answer']}"
                docs.append(Document(page_content=content, metadata={"source": personality_file}))

    return docs

# === Build and Save Vector Store ===
def build_rag_index(character_id):
    character_vector_path = os.path.join(VECTOR_DB_DIR, f"{character_id}_faiss")

    if not os.path.exists(VECTOR_DB_DIR):
        os.makedirs(VECTOR_DB_DIR)

    print(f"📥 Loading documents for {character_id}...")
    documents = load_rag_documents(character_id)

    if not documents:
        print(f"⚠️ No documents found for {character_id}. Skipping index creation.")
        return

    print(f"✅ Loaded {len(documents)} docs. Splitting and embedding...")
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    embedder = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
    vector_store = FAISS.from_documents(chunks, embedder)

    print(f"💾 Saving RAG index for {character_id}...")
    vector_store.save_local(character_vector_path)
    print(f"✅ RAG vector DB saved at: {character_vector_path}")

if __name__ == "__main__":
    # Replace this with a specific character ID if testing
    build_rag_index("default")

def load_retriever(vector_path):
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(
        vector_path,
        embeddings=embedder,
        index_name="index",
        allow_dangerous_deserialization=True  # ✅ Trust your local file
    )
    return vectorstore.as_retriever()
