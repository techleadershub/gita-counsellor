import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch
import sys

# Add backend to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

try:
    from models import VerseChunk, Verse, get_db_engine, get_db_session, Base
    from vector_store import VectorStore
    from ingestion import IngestionService
    from research_agent import ResearchAgent
except ImportError as e:
    # Allow tests to run even if some dependencies are missing
    import warnings
    warnings.warn(f"Some imports failed: {e}")
    VerseChunk = None
    Verse = None
    VectorStore = None
    IngestionService = None
    ResearchAgent = None

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def test_db_path(temp_dir):
    """Path to test SQLite database."""
    return os.path.join(temp_dir, "test_gita.db")

@pytest.fixture
def test_qdrant_path(temp_dir):
    """Path to test Qdrant database."""
    return os.path.join(temp_dir, "test_qdrant")

@pytest.fixture
def mock_db_session(test_db_path, monkeypatch):
    """Create a test database session."""
    monkeypatch.setenv("DB_PATH", test_db_path)
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    session = get_db_session()
    yield session
    session.close()
    os.remove(test_db_path) if os.path.exists(test_db_path) else None

@pytest.fixture
def sample_verse_chunk():
    """Sample verse chunk for testing."""
    return VerseChunk(
        verse_id="BG 2.12",
        chapter=2,
        verse_number=12,
        sanskrit="न त्वेवाहं जातु नासं न त्वं नेमे जनाधिपाः।",
        synonyms="na tu eva—never indeed; aham—I; jātu—at any time; na—never; āsam—existed; na—never; tvam—you; na—never; ime—these; janādhipāḥ—kings",
        translation="Never was there a time when I did not exist, nor you, nor all these kings; nor in the future shall any of us cease to be.",
        purport="This is a very important verse in the Bhagavad Gita..."
    )

@pytest.fixture
def mock_vector_store(test_qdrant_path, monkeypatch):
    """Mock vector store for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    # Create a mock store without initializing the real VectorStore
    store = MagicMock(spec=VectorStore)
    store.collection_name = "test_collection"
    
    # Mock client
    mock_client = MagicMock()
    mock_client.get_collections.return_value = MagicMock(collections=[])
    mock_client.query_points.return_value = MagicMock(points=[])
    mock_client.create_collection = MagicMock()
    store.client = mock_client
    
    # Mock embeddings
    mock_emb = MagicMock()
    mock_emb.embed_query.return_value = [0.1] * 1536
    store.embeddings = mock_emb
    
    # Mock vectorstore
    store.vectorstore = MagicMock()
    store.vectorstore.add_texts = MagicMock()
    
    # Mock methods
    store.add_chunks = MagicMock()
    store.search = MagicMock(return_value=[])
    store.reset_db = MagicMock()
    store._ensure_collection = MagicMock()
    
    yield store

@pytest.fixture
def mock_ingestion_service(mock_vector_store):
    """Mock ingestion service."""
    return IngestionService(mock_vector_store)

@pytest.fixture
def mock_research_agent(mock_vector_store):
    """Mock research agent."""
    with patch('research_agent.ChatOpenAI') as mock_llm:
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        
        # Mock LLM responses
        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_llm_instance.invoke.return_value = mock_message
        
        agent = ResearchAgent(mock_vector_store)
        agent.llm = mock_llm_instance
        yield agent

@pytest.fixture
def sample_verse_data():
    """Sample verse data for database."""
    return {
        "verse_id": "BG 2.12",
        "chapter": 2,
        "verse_number": 12,
        "sanskrit": "न त्वेवाहं जातु नासं",
        "synonyms": "na tu eva—never indeed",
        "translation": "Never was there a time when I did not exist",
        "purport": "This is a very important verse..."
    }

@pytest.fixture
def test_client():
    """FastAPI test client."""
    from main import app
    from fastapi.testclient import TestClient
    return TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch, temp_dir):
    """Set up test environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("DB_PATH", os.path.join(temp_dir, "test.db"))
    monkeypatch.setenv("PORT", "8000")
    # Mock config to avoid reading actual config.yaml
    monkeypatch.setattr("config.LLM_CONFIG", {"openai_key": "test-key", "provider": "openai", "model": "gpt-4o-mini"})
    monkeypatch.setattr("config.VECTOR_DB_CONFIG", {"collection_name": "test_collection", "path": os.path.join(temp_dir, "qdrant")})

