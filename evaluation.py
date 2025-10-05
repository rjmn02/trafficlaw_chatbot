import asyncio
from langchain_groq import ChatGroq
from ragas import evaluate, EvaluationDataset
from ragas.metrics import Faithfulness, ResponseRelevancy
from rag_pipeline import generate_response
from schemas.query import QueryRequest, QueryResponse
from utils.database import async_session
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import HuggingFaceEmbeddings


async def main():
    sample_queries = [
      "Can a motorcycle below 400cc enter expressways in the philippines?",
      "Is it illegal to use a phone while driving in the philippines?",
      "What is the first offense penalty for drunk driving in the philippines?",
    ]
    expected_responses  = [
      "Motorcycles must have at least 400cc engine displacement to use expressways, according to expressway and LTO rules.",
      "Under Republic Act No. 10913, or the Anti-Distracted Driving Act, using mobile phones while driving is prohibited.",
      "3 months imprisonment and a fine of Php 20,000 to Php 80,000, along with a 12-month suspension of the license"
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
      )
    )
    
    # Embedding Evaluator
    embeddings = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")
    
    result = evaluate(
      dataset=evaluation_dataset,
      metrics=[Faithfulness(), ResponseRelevancy()],
      llm=llm_evaluator,
      embeddings=embeddings,
    )
    
    print(result)
if __name__ == "__main__":
    asyncio.run(main())