import uuid
import os
import shutil
from pypdf import PdfReader
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

load_dotenv()
app = FastAPI(title='ATS resume evaluator')


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

class ResumeEvaluation(BaseModel):
    qualification_match: str = Field(description="Analysis of Education and professional Qualification.")
    skill_match: str = Field(description="Analysis of skill matching with the job description.")
    experience_match: str = Field(description="Evaluation of years of experience and domain relevance.")
    overall_match: str = Field(description="Give me a summary of what's missing from it being a good match.")

pc = Pinecone(api_key = os.getenv("PINECONE_API_KEY"))

index_name = "akash-proj-resume-evaluator"

embeddings = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        huggingfacehub_api_token=os.getenv("HF_TOKEN")
    )

def extract_text(file: UploadFile) -> str:
    # Save the file temporarily to disk to avoid FastAPI memory buffer issues
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    text = ""
    try:
        reader = PdfReader(temp_file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        pass
    finally:
        # Clean up the temporary file from your Mac
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    return text

@app.post("/api/evaluate")
async def evaluate_candidate(jd: str = Form(...), resume: UploadFile = File(...)):
    if not resume.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail=" Only pdf is allowed to be uploaded")
    
    raw_text = extract_text(resume)
    print("\n--- EXTRACTED RESUME TEXT ---")
    print(repr(raw_text))
    print("-----------------------------\n")
    if not raw_text or not isinstance(raw_text, str) or raw_text.strip() == "":
        raise HTTPException(
            status_code=400, 
            detail="Could not extract any text from the uploaded resume. Please ensure it is a text-based PDF and not a scanned image."
        )
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 200, chunk_overlap = 40)
    chunks = text_splitter.create_documents([raw_text])

    session_id = str(uuid.uuid4())
    vector_store = PineconeVectorStore.from_documents(
        chunks,
        embedding=embeddings,
        index_name = index_name,
        namespace = session_id
    )
    retriever = vector_store.as_retriever(search_kwargs = {"k": 5})
    relevant_docs = retriever.invoke(jd)
    context_text = "\n\n".join([doc.page_content for doc in relevant_docs])

    llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    structured_llm = llm.with_structured_output(ResumeEvaluation)

    prompt = PromptTemplate(
        template="""You are an expert technical recruiter analyzing a candidate.
        Evaluate the candidate against the Job Description using ONLY the provided Resume Context.
        
        Job Description:
        {jd}
        
        Resume Context:
        {context}
        """,
        input_variables=["jd", "context"]
    )

    chain = prompt|structured_llm
    result = chain.invoke({"jd": jd, "context": context_text})


    pc.Index(index_name).delete(delete_all=True, namespace=session_id)
    return result.model_dump()
if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


    



