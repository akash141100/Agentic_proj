import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(model="openai/gpt-oss-20b", temperature=0,max_tokens=2000)

loader = TextLoader("/Users/akashraj/Desktop/AgenticAI/rules_regulations_extraction_from_sensor_board/cine_act1952_cleaned.pdf")

documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap = 200
)

chunks = text_splitter.split_documents(documents)

print(len(chunks))

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstore = Chroma.from_documents(
    documents= chunks,
    embedding=embeddings,
    persist_directory= "./chroma_db_storage"
)

retriever = vectorstore.as_retriever(search_kwargs={"k":5})

prompt = PromptTemplate.from_template(
    """You are a strict legal and compliance assistant.
    Review the following extracted document segments and identify any rules or regulations regarding obscenity, nudity
    or voilent content. If you are not able to find rules or regulations regardins thes topics, just clearly say that there
    are no rules. Do not invent anything up.

    context: {context}
    question: {question}
    Answer: 
    """
)
parser = StrOutputParser()

rag_chain= (
    {"context": retriever, "question": RunnablePassthrough()}
     |prompt
     |model
     |parser
)

query = ("What are the specific rules and penalties regarding obscenity, nudity and voilent content")

response = rag_chain.invoke(query)
print(response)


