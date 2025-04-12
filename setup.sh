#!/bin/bash
echo Beginning setting up...
echo Installing python requirments...
pip install -r requirements.txt

echo Installing Ollama...
curl -fsSL https://ollama.com/install.sh | sh

echo Pulling Ollama Model...
ollama pull llama3:8b

echo Creating Vector DB from PDFs
python3 pdf_read.py

echo Training AI on AWID CSVs
python3 train_ai.py

echo To use, run "chat_ai.py", and then run "packet_sniffer.py" to begin.
echo Done!
