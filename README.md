# openai-shell

small shell script to interact with openai with conversation history

## Docker
Build the openai-shell binary using docker:
```
make build
```
The binary is written to `./bin/shell`

## Installation
If you wish to install dependencies locally, simply run:
```
pip install -r requirements.txt
touch ~/.cache/openai_query_history
touch ~/.cache/.openai_conversation_history
```

## Run
```
export OPENAI_API_KEY=<your_api_key>
python shell.py
```
