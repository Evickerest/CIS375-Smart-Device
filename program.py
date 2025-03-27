# This package allows us load PDF documents
from langchain_community.document_loaders import PyPDFLoader
import glob

# File path of where our documents are stored
DOCS_PATH = "./docs/"

# This will create a list of all the files under the ./docs/ directory that are pdfs
file_paths = glob.glob(f"{DOCS_PATH}*.pdf")

# Empty list to store our pdfs in
pdfs = []

# Loop through all the files
for file_path in file_paths:
    # Using the PyPDFLoader package, this will load the PDF as an object 
    pages = PyPDFLoader(file_path).load()

    # Add our pages to our pdfs list
    pdfs.append(pages)

# Loop through all the pdfs
for pdf in pdfs:
    # Each pdf contains multiple pages
    for page in pdf:
        # A "page" object contains multiple fields: author, date, size, etc. The actual content of the page is in the "page_content" field
        print(f"Page Content: {page.page_content}\n")



