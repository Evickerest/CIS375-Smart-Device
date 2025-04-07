import glob
from ollama import chat
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# File path of where our documents are stored
DOCS_PATH = "./docs/"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# This will create a list of all the files under the ./docs/ directory that are pdfs
file_paths = glob.glob(f"{DOCS_PATH}*.pdf")

# Empty list to store our pdfs in
pdfs = []

# Loop through all the files
for file_path in file_paths:
    # Using the PyPDFLoader package, this will load the PDF as an object 
    pages = PyPDFLoader(file_path).load()

    # Add all the pages' content to the pdfs list
    pdfs.extend([page.page_content for page in pages])

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
chunks = [chunk for doc in pdfs for chunk in splitter.split_text(doc)]

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
vector_db = FAISS.from_texts(chunks, embeddings)

# Loop while user input is not equal to "q", assign input to variable "user_input"
while ((user_input := input("Enter prompt (q to quit): ")) != "q"):
    # Get relavent chunks based on user input
    relevant_chunks = vector_db.similarity_search(user_input, k=10)

    # Get page content from the relavent pages 
    context = "\n".join([chunk.page_content for chunk in relevant_chunks])

    # Create prompt to the AI 
    prompt = f"""
        You are an AI agent with the purpose of helping the user set up and protect a Smart Home. You have access to the following documents: {context}

        Answer the following question based on the documents and your knowledge: {user_input}"""

    # Create a message in Ollama's format using the prompt 
    message = [{"role": "user", "content": prompt}]
    
    # The "chat" function will query the model running at http://localhost:11434
    # This returns multiple "parts" (i.e., words from the model), which we can loop
    # through and print out the content of the message
    for part in chat('llama3-chatqa', messages=message, stream=True):
      print(part['message']['content'], end='', flush=True)

    # Add some newlines after the AI response
    print("\n\n")
