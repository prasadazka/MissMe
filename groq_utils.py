import os
from langchain_community.chat_models import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

GROQ_API_KEY ="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"
OPENAI_API_KEY ="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"


# Embeddings always use OpenAI
openai_embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

def get_llm_response(prompt: str, model_provider: str) -> str:
    try:
        if model_provider == "Groq (LLaMA3)":
            llm = ChatGroq(
                api_key=GROQ_API_KEY,
                model="llama3-8b-8192"
            )
        elif model_provider == "OpenAI (GPT-4)":
            llm = ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model="gpt-4o"
            )
        elif model_provider == "OpenAI (GPT-3.5)":
            llm = ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model="gpt-4"
            )
        else:
            return "❌ Unknown model selected."

        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)

    except Exception as e:
        print(f"Error calling {model_provider}: {e}")
        return f"⚠️ Error from {model_provider}: {str(e)}"
