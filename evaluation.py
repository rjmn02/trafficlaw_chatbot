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
    "Are 300cc motorcycles allowed on expressways?",
    "What are the penalties for driving without a helmet?",
    "What happens if a driver is caught without a license?",
    "Can a student permit holder drive alone?",
    "What is the minimum engine displacement allowed on expressways?",
    "Is it required to wear a seatbelt while driving?",
    "What are the penalties for reckless driving?",
    "Are back riders required to wear helmets too?",
    "What is the rule for overtaking on solid lines?",
    "What happens if a vehicle is not registered?",
  ]

  expected_responses = [
    "No, motorcycles with an engine displacement of 400cc and above are allowed on expressways. A 300cc motorcycle is not permitted under current LTO and DPWH guidelines.",
    "Driving without a helmet is penalized under the Motorcycle Helmet Act of 2009 with a fine ranging from ₱1,500 to ₱10,000, depending on the number of offenses.",
    "Driving without a valid license is a violation under RA 4136 and carries a fine of ₱3,000 for the driver and possible impoundment of the vehicle.",
    "No, student permit holders are not allowed to drive alone. They must be accompanied by a duly licensed driver seated beside them at all times.",
    "The minimum engine displacement allowed on expressways is 400cc, as set by the Department of Public Works and Highways (DPWH).",
    "Yes, wearing a seatbelt is mandatory for both the driver and front-seat passengers under the Seatbelt Use Act of 1999.",
    "Reckless driving is punishable by fines ranging from ₱2,000 to ₱10,000 and possible suspension or revocation of the driver’s license.",
    "Yes, both the driver and the back rider are required to wear helmets that comply with the DTI-approved ICC mark standards.",
    "Overtaking on solid lines is strictly prohibited under RA 4136. Violators may be fined and cited for reckless or improper overtaking.",
    "Operating an unregistered vehicle is illegal and carries a fine of ₱10,000, along with possible impoundment by the LTO.",
  ]

  dataset = []

  # Inference
  async with async_session() as db:
    for query, reference in zip(sample_queries, expected_responses):
      request = QueryRequest(query=query)
      response: QueryResponse = await generate_response(request, db)
      print(response.answer)

      dataset.append(
        {
          "user_input": query,
          "retrieved_contexts": response.retrieved_docs,
          "response": response.answer,
          "reference": reference,
        }
      )

  evaluation_dataset = EvaluationDataset.from_list(dataset)

  # LLM Evaluator
  llm_evaluator = LangchainLLMWrapper(
    ChatGroq(
      model="llama-3.3-70b-versatile",  # smaller for faster testing
      timeout=500,  # enough time
      temperature=0.1,
    )
  )

  # Use LangChain's HuggingFace embeddings wrapped for compatibility
  langchain_embeddings = LangchainHFEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2", encode_kwargs={"normalize_embeddings": True}
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
