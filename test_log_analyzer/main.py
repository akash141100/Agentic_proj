import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()
model = ChatGroq(model="openai/gpt-oss-20b")

INDEX_NAME = "akash-proj-test-logs-v3"
import json
from langchain_community.document_loaders import TextLoader # Or use JSONLoader
from langchain_core.documents import Document

# Path to your saved JSON file
json_file_path = "/Users/akashraj/Desktop/AgenticAI/test_log_analyzer/cleaned_test_cases.json"

# 1. Load the JSON data
with open(json_file_path, "r", encoding="utf-8") as f:
    cleaned_rows = json.load(f)

# 2. Chunking Strategy: Convert each JSON record into an atomic LangChain Document
chunks = []
for record in cleaned_rows:
    # If your JSON file stores them as plain strings:
    doc = Document(
        page_content=record,
        metadata={"source": "Tosca Test Report JSON"}
    )
    chunks.append(doc)

print(f"Successfully loaded and chunked {len(chunks)} documents from JSON!")

# Example: Print the first chunk
if chunks:
    print("\nSample Loaded Chunk:")
    print(chunks[0].page_content)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vector_store = PineconeVectorStore.from_documents(
    embedding=embeddings,
    index_name=INDEX_NAME,
    documents = chunks

)

retriever = vector_store.as_retriever(search_kwargs={"k":30})

prompt = PromptTemplate.from_template(
    """
You are a senior QA automation engineer who use Tosca. Answer accordingly from the document. If you don't find the answe,
Just say Answer not found. Don't invent anything up.
context: {context}
question:{question}
answer:"""
)

parser = StrOutputParser()

rag_chain = ({"context": retriever, "question": RunnablePassthrough()}
             |prompt
             |model
             |parser

)

query = (" Did test case TC-P2P-SAP-MM-1011 pass or fail, and what was the valuation price? ")

response = rag_chain.invoke(query)
print(response)

# Debug: Print retrieved chunks
retrieved_docs = retriever.invoke(query)
print(f"--- Retrieved {len(chunks) if 'docs' in locals() else len(retrieved_docs)} chunks for query ---")
for i, doc in enumerate(retrieved_docs):
    print(f"Chunk {i+1}: {doc.page_content}\n")


