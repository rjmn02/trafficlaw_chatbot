import asyncio
from langchain_groq import ChatGroq
from ragas import evaluate, EvaluationDataset
from ragas.metrics import Faithfulness, ResponseRelevancy
from rag_pipeline import generate_response
from schemas.query import QueryRequest, QueryResponse
from utils.database import async_session
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_huggingface import HuggingFaceEmbeddings as LangchainHFEmbeddings




async def main():
    sample_queries = [
    "What types of vehicles are prohibited from entering expressways under Department Order No. 123, Series of 2001?",
    "Which government agencies are responsible for implementing and enforcing the rules on limited access highways?",
    "Are pedestrians allowed to cross or walk along expressways in the Philippines?",
    "What is the minimum and maximum speed limit for cars on expressways under DO 123 S.2001?",
    "Can public utility jeepneys (PUJs) use expressways for passenger transport?",
    "What is the primary purpose of establishing limited access highways under DO 123 S.2001?",
    "Are bicycles, animal-drawn vehicles, and handcarts permitted to enter expressways?",
    "Who is authorized to issue and approve regulations governing limited access highways?",
    "Can a motorcycle with 399cc engine displacement legally use an expressway in the Philippines?",
    "Under DO 123 S.2001, what should operators and drivers ensure before entering a limited access highway?"
  ]

    expected_responses = [
      "Vehicles such as tricycles, bicycles, animal-drawn vehicles, handcarts, and motorcycles below 400cc are prohibited from entering expressways under Department Order No. 123, Series of 2001.",
      "The Department of Transportation and Communications (DOTC), Land Transportation Office (LTO), and Toll Regulatory Board (TRB) are responsible for implementing and enforcing the rules on limited access highways.",
      "No. Pedestrians are strictly prohibited from walking or crossing expressways for safety reasons.",
      "For cars, the minimum speed limit is 60 km/h and the maximum is 100 km/h on expressways as prescribed in DO 123 S.2001.",
      "No. Public utility jeepneys are not allowed to use expressways for loading, unloading, or passenger transport.",
      "The primary purpose of establishing limited access highways is to promote safe and efficient movement of traffic by controlling entry and exit points.",
      "No. Bicycles, animal-drawn vehicles, and handcarts are prohibited from entering expressways under Philippine traffic regulations.",
      "The Department of Transportation and Communications (DOTC) is authorized to issue and approve regulations governing limited access highways.",
      "No. Motorcycles must have at least 400cc engine displacement to be legally allowed on expressways.",
      "Operators and drivers must ensure that their vehicles comply with all requirements and safety standards before entering a limited access highway."
    ]


    
    dataset = []

    # Inference
    async with async_session() as db:
      for query,reference in zip(sample_queries,expected_responses):
        request = QueryRequest(query=query)
        response: QueryResponse = await generate_response(request, db)
        print(response.answer)

        dataset.append(
          {
            "user_input":query,
            "retrieved_contexts":response.retrieved_docs,
            "response":response.answer,
            "reference":reference
          }
        )
    
    evaluation_dataset = EvaluationDataset.from_list(dataset)

    # LLM Evaluator
    llm_evaluator = LangchainLLMWrapper(
      ChatGroq(
        model="llama-3.3-70b-versatile",  # smaller for faster testing
        timeout=600,                       # enough time
        temperature=0.1
      )
    )
    
     # Use LangChain's HuggingFace embeddings wrapped for compatibility
    langchain_embeddings = LangchainHFEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    embeddings = LangchainEmbeddingsWrapper(langchain_embeddings)
    
    result = evaluate(
      dataset=evaluation_dataset,
      metrics=[Faithfulness(), ResponseRelevancy(strictness=1)],
      llm=llm_evaluator,
      embeddings=embeddings,
      raise_exceptions=True,
    )
    
    print(result)
if __name__ == "__main__":
    asyncio.run(main())