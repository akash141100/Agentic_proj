import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

# Initialize the Pinecone client
pc = Pinecone(api_key=os.getenv("pcsk_RLJ2M_EFWJ7Eti9LBMVwDsVnUe8GMQX3QUSxkUCE2fGxV7ZSKdymLiZJMUNKZ1Q6ZhEhx"))

# Create a classic, schema-free vector index
pc.create_index(
    name="akash-proj1",
    dimension=384,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

print("Standard vector index created successfully!")