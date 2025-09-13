from langchain_huggingface import HuggingFaceEmbeddings

def get_embedding_model(
  model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
) -> HuggingFaceEmbeddings:
  return HuggingFaceEmbeddings(model_name=model_name)