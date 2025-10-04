from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from embedding_model import get_embedding_model
from vector_store import get_vector_store
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# Configuration constants
MODEL_NAME = "llama-3.1-8b-instant"
# MODEL_NAME = "llama-3.3-70b-versatile"
MODEL_PROVIDER = "groq"
COLLECTION_NAME = "trafficlaw_docs"
RETRIEVAL_K = 3


# load pipeline components
llm = init_chat_model(MODEL_NAME, model_provider=MODEL_PROVIDER)
embedding_model = get_embedding_model()
vector_store = get_vector_store(
  embeddings=embedding_model,
  collection_name=COLLECTION_NAME,
)

def prompt_augmentation(query: str, context: str) -> str:
  template = """
  You are a Philippine Traffic Law Chatbot that provides reliable, contextually grounded information about traffic laws and vehicle regulations in the Philippines.
  Follow these rules strictly when answering:

  - Use only the provided context to generate responses. If the answer is not in the context, say: “I don't know the answer based on Philippine traffic laws.”
  - Always stay within the scope: Philippine traffic and vehicle regulations only. Do not provide unrelated legal or personal advice.
  - Be clear, neutral, and user-friendly in tone.
  - At the start of each conversation, remind the users: “This chatbot is for informational purposes only and not a substitute for professional legal advice.”
  - 
  Context:
  {context}

  User Query:
  {query}

  Answer:"""
  
  return ChatPromptTemplate.from_template(template)

def build_rag(query: str):
