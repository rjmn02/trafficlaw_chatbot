# analyze_chunks.py
from vector_store import get_vector_store
from embedding_model import get_embedding_model
from transformers import AutoTokenizer
import csv

def analyze_data():
    # init vector store
    embedding_model = get_embedding_model()
    vector_store = get_vector_store(
        embeddings=embedding_model,
        collection_name="trafficlaw_docs",  # same as what you used when storing
    )

    # load docs back
    docs = vector_store.similarity_search("penalties", k=50)  # grab some docs

    # check chunk token lengths
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    lengths = [len(tokenizer.encode(d.page_content)) for d in docs]

    print("Number of docs retrieved:", len(docs))
    print("Min tokens:", min(lengths))
    print("Max tokens:", max(lengths))
    print("Avg tokens:", sum(lengths) / len(lengths))
    
    # export to CSV
    with open("analyze_output.csv", mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["chunk_text", "token_count", "metadata"])

        for d, length in zip(docs, lengths):
            writer.writerow([d.page_content, length, d.metadata])

    # # optional: print a sample
    # for d in docs[40:43]:
    #     print("\n--- SAMPLE CHUNK ---")
    #     print(d.page_content[:500])  # print first 500 chars
    #     print("Metadata:", d.metadata)

if __name__ == "__main__":
    analyze_data()
