import yaml
import os
from pathlib import Path

# Try to find config.yaml in probable locations
search_paths = [
    Path(__file__).parent / "config.yaml",
    Path(__file__).parent.parent / "config.yaml"
]

CONFIG_PATH = None
for p in search_paths:
    if p.exists():
        CONFIG_PATH = p
        break

def load_config():
    if CONFIG_PATH and CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)
    return {}

config = load_config()

# Helper to get specific sections with Env Var overrides
LLM_CONFIG = config.get("llm", {})
# Env Var Overrides for LLM
if os.getenv("OPENAI_API_KEY"):
    LLM_CONFIG["openai_key"] = os.getenv("OPENAI_API_KEY")
if os.getenv("OPENROUTER_API_KEY"):
    LLM_CONFIG["openrouter_key"] = os.getenv("OPENROUTER_API_KEY")

VECTOR_DB_CONFIG = config.get("vector_db", {})
# Environment variables take precedence over YAML config
# Priority: QDRANT_URL > QDRANT_HOST > YAML config > local embedded
qdrant_url = os.getenv("QDRANT_URL")
qdrant_host = os.getenv("QDRANT_HOST")

if qdrant_url:
    # Docker/Railway mode - use URL connection (full URL provided)
    # Extract host and port from URL if not separately provided
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    parsed_host = qdrant_host or "qdrant"
    VECTOR_DB_CONFIG = {
        "collection_name": VECTOR_DB_CONFIG.get("collection_name", "bhagavad_gita_verses"),
        "url": qdrant_url,  # Use the full URL directly
        "host": parsed_host,
        "port": qdrant_port
    }
elif qdrant_host:
    # Docker mode - use host:port connection (construct URL)
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    VECTOR_DB_CONFIG = {
        "collection_name": VECTOR_DB_CONFIG.get("collection_name", "bhagavad_gita_verses"),
        "url": f"http://{qdrant_host}:{qdrant_port}",
        "host": qdrant_host,
        "port": qdrant_port
    }
elif not VECTOR_DB_CONFIG or "path" not in VECTOR_DB_CONFIG:
    # If no YAML config or no path in YAML, use local embedded as default
    if not VECTOR_DB_CONFIG:
        VECTOR_DB_CONFIG = {}
    if "path" not in VECTOR_DB_CONFIG:
        VECTOR_DB_CONFIG["path"] = "./data/qdrant_db"
    if "collection_name" not in VECTOR_DB_CONFIG:
        VECTOR_DB_CONFIG["collection_name"] = "bhagavad_gita_verses"

APP_CONFIG = config.get("app", {})

# SQLite Database path
DB_PATH = os.getenv("DB_PATH", "./data/gita_verses.db")

