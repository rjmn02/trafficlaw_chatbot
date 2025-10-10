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
    "Are 300cc motorcycles allowed in expressways in the Philippines?",
    "What are the penalties for driving without a helmet in the Philippines?",
    "What are the penalties for driving without a license in the Philippines?",
    "What is the maximum speed limit on Philippine expressways?",
    "Can I use my phone while driving in the Philippines?",
    "What is the blood alcohol content (BAC) limit for drivers in the Philippines?",
    "Do I need to carry a fire extinguisher in my vehicle in the Philippines?",
    "What are the penalties for running a red light in the Philippines?",
    "Is it legal to make a U-turn at any intersection in the Philippines?",
    "What documents must I carry while driving in the Philippines?",
  ]

  expected_responses = [
    "No, motorcycles with engine displacement of 400cc or higher are allowed on most Philippine expressways like NLEX, SLEX, and TPLEX. However, 300cc motorcycles are generally NOT allowed as they fall below the minimum requirement. Some tollways have specific restrictions, so it's best to check with the particular expressway operator. Smaller motorcycles must use alternative routes.",
    "Under Republic Act 10054 (Motorcycle Helmet Act of 2009), riding without a helmet carries a fine of PHP 1,500 for the first offense, PHP 3,000 for the second offense, and PHP 5,000 for the third offense. Additionally, the driver's license may be confiscated and the motorcycle may be impounded. Both the driver and the backrider must wear standard protective helmets.",
    "Driving without a license in the Philippines is punishable under RA 4136 (Land Transportation and Traffic Code). Penalties include: imprisonment of not less than one month but not more than six months, or a fine ranging from PHP 3,000 to PHP 20,000, or both. The vehicle may also be impounded. For professional drivers caught without a license, penalties are more severe.",
    "The maximum speed limit on Philippine expressways is typically 100 km/h for cars and light vehicles, and 80 km/h for trucks and buses. However, specific expressways may have different posted limits. Minimum speed is usually 60 km/h. Speed limits may be reduced in certain sections such as construction zones, curves, or approaches to toll plazas.",
    "No, using a mobile phone while driving is prohibited under RA 10913 (Anti-Distracted Driving Act). This includes making calls, texting, browsing, or any use of communication devices while the vehicle is in motion or temporarily stopped at a traffic light. Penalties range from PHP 5,000 for the first offense to PHP 15,000 and license suspension for subsequent offenses. Hands-free devices are allowed.",
    "The legal blood alcohol content (BAC) limit in the Philippines is 0.05% for private vehicle drivers and 0.00% (zero tolerance) for professional drivers under RA 10586 (Anti-Drunk and Drugged Driving Act of 2013). Violators face fines ranging from PHP 20,000 to PHP 500,000, imprisonment from three months to 20 years depending on circumstances, and license suspension or revocation.",
    "Yes, under RA 4136 and its implementing rules, private cars are required to carry a serviceable fire extinguisher (minimum 1kg dry chemical type), an early warning device (EWD), and a first aid kit. Non-compliance can result in fines and the vehicle failing roadworthiness inspections during LTO registration renewal.",
    "Running a red light is a violation of RA 4136. Penalties include a fine of PHP 1,000 and potential license suspension or revocation for repeat offenses. The violation also carries corresponding demerit points under the LTO's demerit system. In areas with traffic enforcement cameras (No Contact Apprehension Policy), violators receive tickets by mail.",
    "No, U-turns are only allowed where explicitly permitted by signage or road markings. U-turns are generally prohibited at intersections with traffic lights unless there's a specific 'U-Turn Allowed' sign, on bridges, at railroad crossings, in tunnels, and where visibility is limited. Illegal U-turns carry a fine of PHP 1,000 and may result in license demerit points.",
    "Drivers in the Philippines must carry: (1) valid driver's license, (2) Official Receipt (OR) of vehicle registration, (3) Certificate of Registration (CR), and for certain vehicles (4) Certificate of Emission Compliance. Professional drivers must also carry their Professional Driver's Badge. Failure to present these documents when flagged by authorities can result in fines, vehicle impoundment, or both.",
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
      timeout=5000,  # enough time
      temperature=0.0,
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
