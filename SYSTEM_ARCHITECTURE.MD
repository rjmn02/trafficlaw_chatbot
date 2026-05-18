# System Architecture

## Overview
The architecture represents a Retrieval-Augmented Generation (RAG) pipeline for a Traffic Law Chatbot. 

## Architecture Diagram

`mermaid
flowchart LR
    %% Data Sources
    subgraph Data_Source ["Data Source"]
        PD[(Public Data)] --> TL[(Traffic Laws and LTO Handbook)]
    end

    %% Pre-processing
    subgraph PreProcessing ["Data Pre-Processing Module"]
        direction TB
        TC[Text Chunking] --> EM[Embedding Model<br>all-MiniLM-L6-v2]
    end
    
    %% Note about embeddings
    Note1>The embedding model is used for<br>both data documents and<br>query embeddings.] -.-> PreProcessing

    %% Vector DB
    VDB[(VECTOR DB)]

    %% RAG Pipeline
    subgraph RAG ["RAG Pipeline Module"]
        direction TB
        SS[Similarity Search &<br>Query Embedding] --> PA[/Prompt Augmented/]
        PA --> ResGen[Response Generation<br>LLM]
        ResGen --> Llama[Llama 3.1 via Groq API]
    end

    %% Chatbot Interface
    subgraph Interface ["Chatbot Interface"]
        UQ([User Query / Legal Response])
    end

    %% Evaluation
    subgraph Evaluation ["Evaluation"]
        KA[Krippendorff's alpha]
        US[User Survey]
    end

    %% Flow connections
    Data_Source <--> PreProcessing
    EM -->|Input| VDB
    VDB -->|Output| RAG
    Interface <--> RAG
    RAG <--> Evaluation
`

## Module Breakdown

1. **Data Source**: Pulls **Public Data** (specifically Traffic Laws and the LTO Handbook).
2. **Data Pre-Processing Module**: 
   - **Text Chunking:** Breaks the handbook into manageable text chunks.
   - **Embedding Model:** Generates semantic vectors using ll-MiniLM-L6-v2. (Note: The same model is utilized for both data documents and user query embeddings).
3. **VECTOR DB**: The central vector database that stores structural data vectors created by the preprocessing module.
4. **RAG Pipeline Module**:
   - Takes output from Vector DB.
   - Converts the incoming query into embeddings and performs a **Similarity Search**.
   - Builds an **Augmented Prompt** based on the results.
   - Passes the augmented prompt to the **Response Generation (LLM)**, powered by **Llama 3.1 via the Groq API**.
5. **Chatbot Interface**: Translates user inputs (User Query) and displays the generated output (Legal Response).
6. **Evaluation**: Provides benchmarking and validation of the LLM output via **Krippendorff's alpha** (for inter-rater reliability) and a **User Survey**.
