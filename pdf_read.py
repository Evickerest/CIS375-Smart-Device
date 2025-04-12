import glob
from ollama import chat
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from pickle import dump

# File path of where our documents are stored
DOCS_PATH = "./docs/"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# This will create a list of all the files under the ./docs/ directory that are pdfs
file_paths = glob.glob(f"{DOCS_PATH}*.pdf")

# Empty list to store our pdfs in
pdfs = []

print("Loading PDFs...\n")

# Loop through all the files
for file_path in file_paths:
    # Using the PyPDFLoader package, this will load the PDF as an object 
    pages = PyPDFLoader(file_path).load()

    # Add all the pages' content to the pdfs list
    pdfs.extend([page.page_content for page in pages])

print("Splitting PDFs into Chunks...\n")

# Goes over all the pages and splits the text into 500 character sized chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
chunks = [chunk for doc in pdfs for chunk in splitter.split_text(doc)]

print("Creating VectorDB from Chunks...\n")

# Creates a Model that can be queried to find similiar text
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
vector_db = FAISS.from_texts(chunks, embeddings)

print("Writing to file...\n")

# Writes the vectorDb to fiel so we don't have to go through all the work of recreating it later
with open("./models/vector.pkl", "wb") as file:
    dump(vector_db, file, protocol=5)

print("Done.")



