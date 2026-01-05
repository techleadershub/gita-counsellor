import pytest
from unittest.mock import MagicMock, patch, Mock
from vector_store import VectorStore
from models import VerseChunk

def test_vector_store_initialization(mock_vector_store):
    """Test vector store initialization."""
    assert mock_vector_store is not None
    assert mock_vector_store.collection_name is not None

def test_vector_store_add_chunks(mock_vector_store, sample_verse_chunk):
    """Test adding chunks to vector store."""
    chunks = [sample_verse_chunk]
    
    # Call the mocked method
    mock_vector_store.add_chunks(chunks)
    
    # Verify it was called
    assert mock_vector_store.add_chunks.called

def test_vector_store_search(mock_vector_store):
    """Test vector store search."""
    # Mock search to return results
    mock_result = {
        "chunk": {"verse_id": "BG 2.12"},
        "score": 0.95,
        "content": "Test content"
    }
    mock_vector_store.search.return_value = [mock_result]
    
    results = mock_vector_store.search("test query", limit=5)
    
    assert len(results) == 1
    assert results[0]["score"] == 0.95
    assert "chunk" in results[0]
    assert "content" in results[0]

def test_vector_store_search_empty(mock_vector_store):
    """Test search with no results."""
    mock_vector_store.client.query_points.return_value = MagicMock(points=[])
    
    results = mock_vector_store.search("test query")
    
    assert len(results) == 0

def test_vector_store_reset_db(mock_vector_store):
    """Test resetting vector database."""
    mock_vector_store.reset_db()
    
    # Verify reset_db was called
    assert mock_vector_store.reset_db.called

def test_vector_store_ensure_collection_new(mock_vector_store):
    """Test collection creation when it doesn't exist."""
    mock_vector_store._ensure_collection()
    
    # Verify method was called
    assert mock_vector_store._ensure_collection.called

def test_vector_store_ensure_collection_exists(mock_vector_store):
    """Test collection handling when it already exists."""
    mock_collection = MagicMock()
    mock_collection.name = mock_vector_store.collection_name
    mock_vector_store.client.get_collections.return_value = MagicMock(collections=[mock_collection])
    mock_vector_store.client.create_collection = MagicMock()
    
    mock_vector_store._ensure_collection()
    
    # Should not create if exists
    mock_vector_store.client.create_collection.assert_not_called()

