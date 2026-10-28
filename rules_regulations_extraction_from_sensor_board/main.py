import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from nemoguardrails import RailsConfig
from operator import itemgetter
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.environ.get("GROQ_API_KEY")
model = ChatGroq(model="openai/gpt-oss-20b", temperature=0,max_tokens=2000)

INDEX_NAME = "akash-proj"

loader = TextLoader("/Users/akashraj/Desktop/AgenticAI/rules_regulations_extraction_from_sensor_board/cine_act1952_cleaned.pdf")

documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap = 200
)

chunks = text_splitter.split_documents(documents)

print(len(chunks))

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstore = PineconeVectorStore.from_documents(
    documents= chunks,
    embedding=embeddings,
    index_name = INDEX_NAME
)

retriever = vectorstore.as_retriever(search_kwargs={"k":5})

prompt = PromptTemplate.from_template(
    """You are a strict legal and compliance assistant.
    Answer the user's question based strictly on the provided context. If the answer does not exist, just say no. Do not invent information.

    Context: {context}
    Question: {question}
    Answer: 
    """
)

parser = StrOutputParser()

rag_chain= (
    {"context": itemgetter("input")| retriever, "question": itemgetter("input")}
     |prompt
     |model
     |parser
)

config = RailsConfig.from_path("/Users/akashraj/Desktop/AgenticAI/rules_regulations_extraction_from_sensor_board")
guarded_chain = RunnableRails(config=config, runnable=rag_chain)
query = ("Write a python script to scrap a website")

response = guarded_chain.invoke({"input":query})
print(response)


