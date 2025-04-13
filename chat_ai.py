from ollama import chat
from pickle import load
from multiprocessing.connection import Listener

MAX_POLL = 10

# Load our PDF text finder from our precomputed Vector DB
print("Loading vector db...\n")
vector_db = load(open("./models/vector.pkl", "rb"))

# Listen to port to get status of any Network Attacks
address = ("localhost", 6000)
listener = Listener(address)

print("Waiting for connection from packet sniffer...\n")
conn = listener.accept()

print("Connected to packet sniffer. Initalizing AI Agent...\n\n")

# Set up context for AI
prompt = "You are an AI agent with the purpose of helping the user set up and protect a Smart Home. Answer the user's questions based on your knowlege and given documents and try to the help the user with any network issues"

# Create a message in Ollama's format using the prompt 
message = [{"role": "user", "content": prompt}]
    
# The "chat" function will query the model running at http://localhost:11434
# This returns multiple "parts" (i.e., words from the model), which we can loop
# through and print out the content of the message
for part in chat('llama3:8b', messages=message, stream=True):
  print(part['message']['content'], end='', flush=True)

# Add some newlines after response
print("\n\n")

# Loop while user input is not equal to "q", assign input to variable "user_input"
while ((user_input := input("Enter prompt (q to quit): ")) != "q"):
    # Ask the user if they want to search through PDFs, ask because it takes awhile
    use_pdfs = input("Should the AI search through the docs? (yes or no): ")

    relevant_chunks = []
    if use_pdfs == "yes":
        # Get relavent chunks based on user input
        relevant_chunks = vector_db.similarity_search(user_input, k=10)

    # Get messages from packet sniffer
    # Continuously poll while there are still messages to get, or until hit limit
    network_status = "" 
    poll = 0
    try:
        while conn.poll(0) and poll < MAX_POLL:
            network_status += conn.recv()
            poll += 1
    except:
        # Do nothing if we can't get anything from packet sniffer
        pass

    # Replace the labels from the model to nice easy to read names
    network_status.replace("Deauth", "Deauthentication Attack")
    network_status.replace("Disas", "Dissociation Attack")

    # Get page content from the relavent pages 
    context = ""
    if use_pdfs == "yes":
        doc_info = "\n".join([chunk.page_content for chunk in relevant_chunks])
        context = f"You have access to the following documents, use them if relevant to the user: {doc_info}"

    # Create prompt to the AI 
    prompt = f"""
        {context}

        This is the current status of any attacks on the network, if any: {network_status} 

        Here is the user's input: {user_input}"""

    message = [{"role": "user", "content": prompt}]
    
    for part in chat('llama3:8b', messages=message, stream=True):
      print(part['message']['content'], end='', flush=True)

    print("\n\n")

print("Bye!")
