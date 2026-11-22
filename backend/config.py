import os

# Ollama connection (can be overridden with environment variables, e.g. in Docker)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Models
CHAT_MODEL = os.getenv("PAPERPILOT_CHAT_MODEL", "llama3.2:1b")
EMBED_MODEL = os.getenv("PAPERPILOT_EMBED_MODEL", "nomic-embed-text")

# Summarisation
SECTION_CHARS = 6000      # max characters per section in map-reduce

# Question answering (used from tomorrow)
CHUNK_CHARS = 1000        # size of each chunk
CHUNK_OVERLAP = 150       # characters shared between neighbouring chunks
TOP_K = 4                 # how many chunks to give the model