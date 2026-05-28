
#!/bin/sh

ollama serve &

# wait for server to start
sleep 5

ollama pull llama3.2

wait