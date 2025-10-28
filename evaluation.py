import asyncio
from langchain_groq import ChatGroq
from ragas import evaluate, EvaluationDataset
from ragas.metrics import Faithfulness, ResponseRelevancy
from rag_pipeline import generate_response
from schemas.query import QueryRequest, QueryResponse
from utils.database import async_session
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings as LangchainHFEmbeddings
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

TESTSET_FILEPATH = os.getenv("EVAL_TESTSET_PATH", " ")


async def main():
  df = pd.read_csv(TESTSET_FILEPATH)
  user_input = df["user_query"].tolist()
  expected_responses = df["expected_responses"].tolist()
  dataset = []

  # Inference
  async with async_session() as db:
    for query, reference in zip(user_input, expected_responses):
      session_id = str(uuid.uuid4())
      request = QueryRequest(query=query, session_id=session_id)
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
      timeout=70000,  # enough time
      temperature=0.0,
      max_retries=5,
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
  
  df_res = result.to_pandas()
  df_res.to_csv(os.getenv("EVAL_RESULT_PATH"), index=False)

  print(result)


if __name__ == "__main__":
  asyncio.run(main())
