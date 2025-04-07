#!/bin/bash
echo Setting up...
pip install -r requirements.txt
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3-chatqa:8b
echo Done!
