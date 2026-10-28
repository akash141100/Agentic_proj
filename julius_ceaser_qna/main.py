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
model = ChatGroq(model="openai/gpt-oss-20b", max_tokens= 2000)

INDEX_NAME = "akash-proj1"

loader = TextLoader("/Users/akashraj/Desktop/AgenticAI/julius_ceaser_qna/julius_ceaser_cleaned.pdf")
documents = loader.load()

test_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200
)

chunks = test_splitter.split_documents(documents)

print(len(chunks))

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vector_database = PineconeVectorStore.from_documents(
    embedding=embeddings,
    documents=chunks,
    index_name=INDEX_NAME
)

retriever = vector_database.as_retriever(search_kwargs={"k":5})

prompt = PromptTemplate.from_template("""
You are an Englist literature expet. So answer the questions accordingly. Just reply answers not found if you do not 
find answers from the data source given. Do not invent the answer.
context:{context}
question:{question}
answer:
"""
)
parser = StrOutputParser()

rag_chain = ({"context": retriever, "question": RunnablePassthrough()}
             |prompt
             |model
             |parser
             
)

query = ("Why do the conspirators decide that Julius Caesar must be assassinated?")

response = rag_chain.invoke(query)
print(response)


