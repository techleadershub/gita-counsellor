import pytest
from unittest.mock import MagicMock, patch, Mock
import sys
import os

# Ensure we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def client():
    """Create test client."""
    from starlette.testclient import TestClient
    from main import app
    # TestClient from starlette should work
    return TestClient(app)

def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@patch('main.get_vector_store')
@patch('main.ResearchAgent')
def test_research_endpoint(mock_agent_class, mock_vector_store, client):
    """Test research endpoint."""
    # Mock vector store
    mock_vs = MagicMock()
    mock_vector_store.return_value = mock_vs
    
    # Mock agent
    mock_agent = MagicMock()
    mock_graph = MagicMock()
    mock_state = {
        "final_answer": "# Test Answer\n\nThis is a test answer.",
        "analysis": "Test analysis",
        "guidance": "Test guidance",
        "exercises": "Test exercises",
        "relevant_verses": [{"verse_id": "BG 2.12"}]
    }
    mock_graph.invoke.return_value = mock_state
    mock_agent.build_graph.return_value = mock_graph
    mock_agent_class.return_value = mock_agent
    
    response = client.post("/api/research", json={
        "query": "How to deal with stress?",
        "context": None
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "analysis" in data
    assert "guidance" in data
    assert "exercises" in data
    assert "verses" in data

def test_research_endpoint_missing_query(client):
    """Test research endpoint with missing query."""
    response = client.post("/api/research", json={})
    assert response.status_code == 422  # Validation error

@patch('main.get_db_session')
def test_get_verses_endpoint(mock_db_session, client):
    """Test get verses endpoint."""
    # Mock database session
    mock_verse = MagicMock()
    mock_verse.to_dict.return_value = {
        "verse_id": "BG 2.12",
        "chapter": 2,
        "verse_number": 12,
        "translation": "Test translation"
    }
    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.all.return_value = [mock_verse]
    mock_db_session.return_value = mock_session
    
    response = client.get("/api/verses?chapter=2")
    
    assert response.status_code == 200
    data = response.json()
    assert "verses" in data
    assert len(data["verses"]) > 0

@patch('main.get_db_session')
def test_get_verse_by_id_endpoint(mock_db_session, client):
    """Test get verse by ID endpoint."""
    mock_verse = MagicMock()
    mock_verse.to_dict.return_value = {
        "verse_id": "BG 2.12",
        "chapter": 2,
        "verse_number": 12,
        "translation": "Test translation"
    }
    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_verse
    mock_db_session.return_value = mock_session
    
    response = client.get("/api/verses/BG%202.12")
    
    assert response.status_code == 200
    data = response.json()
    assert "verse" in data
    assert data["verse"]["verse_id"] == "BG 2.12"

@patch('main.get_db_session')
def test_get_verse_by_id_not_found(mock_db_session, client):
    """Test get verse by ID when not found."""
    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    mock_db_session.return_value = mock_session
    
    response = client.get("/api/verses/BG%20999.999")
    
    assert response.status_code == 404

@patch('main.IngestionService')
@patch('main.get_vector_store')
def test_ingest_endpoint(mock_vector_store, mock_service_class, client):
    """Test ingestion endpoint."""
    mock_vs = MagicMock()
    mock_vector_store.return_value = mock_vs
    
    mock_service = MagicMock()
    mock_service.ingest_epub.return_value = 100
    mock_service_class.return_value = mock_service
    
    response = client.post("/api/ingest", json={"epub_path": None})
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "100" in data["message"]

def test_ingestion_status_endpoint(client):
    """Test ingestion status endpoint."""
    response = client.get("/api/ingestion/status")
    assert response.status_code == 200
    assert "status" in response.json()

@patch('main.get_db_session')
@patch('main.get_vector_store')
def test_stats_endpoint(mock_vector_store, mock_db_session, client):
    """Test stats endpoint."""
    # Mock database
    mock_verse = MagicMock()
    mock_session = MagicMock()
    mock_session.query.return_value.count.return_value = 700
    mock_session.query.return_value.distinct.return_value.count.return_value = 18
    mock_db_session.return_value = mock_session
    
    # Mock vector store
    mock_vs = MagicMock()
    mock_collection = MagicMock()
    mock_collection.points_count = 700
    mock_vs.client.get_collections.return_value = MagicMock(collections=[mock_collection])
    mock_vs.collection_name = "test_collection"
    mock_vs.client.get_collection.return_value = mock_collection
    mock_vector_store.return_value = mock_vs
    
    response = client.get("/api/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert "total_verses" in data
    assert "chapters" in data
    assert "vector_store_points" in data

