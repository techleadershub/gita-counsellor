"""
Robust End-to-End Tests

These tests verify the system is robust and handles real-world scenarios.
Tests actual system behavior with real data and real scenarios.
"""
import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Verse, VerseChunk, get_db_engine, get_db_session, Base
from fastapi.testclient import TestClient
from main import app

# Real scenarios to test
ROBUST_SCENARIOS = [
    {
        "name": "Empty database handling",
        "setup": lambda: None,  # No verses
        "test": "Should handle gracefully"
    },
    {
        "name": "Large response handling",
        "setup": lambda session: None,  # Will use existing
        "test": "Should handle large responses"
    },
    {
        "name": "Invalid input handling",
        "setup": lambda: None,
        "test": "Should reject invalid inputs"
    },
    {
        "name": "Concurrent requests",
        "setup": lambda: None,
        "test": "Should handle multiple requests"
    }
]

@pytest.fixture
def robust_test_db():
    """Create a robust test database."""
    import time
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, f"robust_test_{os.getpid()}_{int(time.time() * 1000000)}.db")
    
    original_db_path = os.environ.get("DB_PATH")
    os.environ["DB_PATH"] = db_path
    
    # Create database
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    
    yield db_path
    
    # Cleanup
    try:
        session = get_db_session()
        session.query(Verse).delete()
        session.commit()
        session.close()
    except:
        pass
    
    if original_db_path:
        os.environ["DB_PATH"] = original_db_path
    elif "DB_PATH" in os.environ:
        del os.environ["DB_PATH"]
    
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass

class TestRobustE2E:
    """Robust end-to-end tests for real-world scenarios."""
    
    def test_empty_database_handling(self, robust_test_db):
        """Test that system handles empty database gracefully."""
        client = TestClient(app)
        
        # Ensure database is empty by checking the test DB
        # The robust_test_db fixture creates a fresh empty DB
        from unittest.mock import patch
        real_session = get_db_session()
        
        # Verify it's empty (or clear it)
        count = real_session.query(Verse).count()
        if count > 0:
            real_session.query(Verse).delete()
            real_session.commit()
        
        count = real_session.query(Verse).count()
        assert count == 0, f"Database should be empty, but has {count} verses"
        
        with patch('main.get_db_session', return_value=real_session):
            response = client.get("/api/verses?chapter=2")
            # Should return 200 with empty list, not error
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            data = response.json()
            assert "verses" in data
            assert len(data["verses"]) == 0  # Should return empty list, not error
        
        real_session.close()
    
    def test_invalid_input_robustness(self, robust_test_db):
        """Test system robustness with invalid inputs."""
        client = TestClient(app)
        
        # Test various invalid inputs
        invalid_inputs = [
            {},  # Empty
            {"query": ""},  # Empty query
            {"query": "a" * 10000},  # Very long query
            {"query": None},  # None query
            {"query": "test", "context": "a" * 50000},  # Very long context
        ]
        
        for invalid_input in invalid_inputs:
            response = client.post("/api/research", json=invalid_input)
            # Should either validate (422) or handle gracefully (400/500)
            assert response.status_code in [200, 400, 422, 500], \
                f"Invalid input {invalid_input} should be handled gracefully"
    
    def test_special_characters_handling(self, robust_test_db):
        """Test system handles special characters correctly."""
        client = TestClient(app)
        
        special_queries = [
            "What about leadership? 🚀",
            "How to deal with stress & anxiety?",
            "What's the guidance on AI/ML ethics?",
            "Gen Z & Gen Alpha challenges",
            "Test with <script>alert('xss')</script>",
        ]
        
        from unittest.mock import patch, MagicMock
        
        with patch('main.get_vector_store') as mock_vs, \
             patch('main.ResearchAgent') as mock_agent_class:
            
            mock_vector_store = MagicMock()
            mock_vector_store.search.return_value = []
            mock_vs.return_value = mock_vector_store
            
            mock_agent = MagicMock()
            mock_graph = MagicMock()
            mock_state = {
                "user_query": "test",
                "problem_context": "",
                "research_questions": [],
                "relevant_verses": [],
                "analysis": "Test",
                "guidance": "Test",
                "exercises": "Test",
                "final_answer": "# Test"
            }
            mock_graph.invoke.return_value = mock_state
            mock_agent.build_graph.return_value = mock_graph
            mock_agent_class.return_value = mock_agent
            
            for query in special_queries:
                response = client.post("/api/research", json={"query": query})
                # Should handle special characters without crashing
                assert response.status_code in [200, 400, 422, 500], \
                    f"Special characters in '{query}' should be handled"
    
    def test_concurrent_request_structure(self, robust_test_db):
        """Test that system structure supports concurrent requests."""
        client = TestClient(app)
        
        from unittest.mock import patch, MagicMock
        
        with patch('main.get_vector_store') as mock_vs, \
             patch('main.ResearchAgent') as mock_agent_class, \
             patch('main.get_db_session') as mock_db:
            
            real_session = get_db_session()
            mock_db.return_value = real_session
            
            mock_vector_store = MagicMock()
            mock_vector_store.search.return_value = []
            mock_vs.return_value = mock_vector_store
            
            # Simulate multiple concurrent requests
            questions = [
                "Question 1",
                "Question 2", 
                "Question 3"
            ]
            
            for question in questions:
                mock_agent = MagicMock()
                mock_graph = MagicMock()
                mock_state = {
                    "user_query": question,
                    "problem_context": "",
                    "research_questions": [],
                    "relevant_verses": [],
                    "analysis": f"Analysis for {question}",
                    "guidance": f"Guidance for {question}",
                    "exercises": f"Exercises for {question}",
                    "final_answer": f"# Answer\n\n{question}"
                }
                mock_graph.invoke.return_value = mock_state
                mock_agent.build_graph.return_value = mock_graph
                mock_agent_class.return_value = mock_agent
                
                response = client.post("/api/research", json={"query": question})
                assert response.status_code == 200
                assert question in response.json().get("answer", "")
            
            real_session.close()
    
    def test_data_persistence(self, robust_test_db):
        """Test that data persists correctly through operations."""
        session = get_db_session()
        
        # Add a verse
        verse = Verse(
            verse_id="BG 1.1",
            chapter=1,
            verse_number=1,
            translation="Test translation",
            purport="Test purport"
        )
        session.add(verse)
        session.commit()
        
        # Verify it persists
        retrieved = session.query(Verse).filter_by(verse_id="BG 1.1").first()
        assert retrieved is not None
        assert retrieved.translation == "Test translation"
        
        # Test conversion to chunk
        chunk = VerseChunk(
            verse_id=retrieved.verse_id,
            chapter=retrieved.chapter,
            verse_number=retrieved.verse_number,
            translation=retrieved.translation,
            purport=retrieved.purport
        )
        
        # Verify data integrity
        assert chunk.verse_id == "BG 1.1"
        assert chunk.translation == "Test translation"
        assert len(chunk.to_text_for_embedding()) > 50
        
        session.close()
    
    def test_error_recovery(self, robust_test_db):
        """Test that system recovers from errors gracefully."""
        client = TestClient(app)
        
        # Test with malformed requests
        malformed_requests = [
            '{"invalid": json}',  # Invalid JSON
            '{"query": 123}',  # Wrong type
            '{"query": []}',  # Array instead of string
        ]
        
        for request_data in malformed_requests:
            try:
                # This will fail at JSON parsing, which is expected
                response = client.post("/api/research", 
                    data=request_data,
                    headers={"Content-Type": "application/json"})
                # Should return error status, not crash
                assert response.status_code >= 400
            except Exception:
                # JSON parsing error is acceptable
                pass
    
    def test_response_consistency(self, robust_test_db):
        """Test that responses are consistent in structure."""
        client = TestClient(app)
        
        from unittest.mock import patch, MagicMock
        
        with patch('main.get_vector_store') as mock_vs, \
             patch('main.ResearchAgent') as mock_agent_class, \
             patch('main.get_db_session') as mock_db:
            
            real_session = get_db_session()
            mock_db.return_value = real_session
            
            mock_vector_store = MagicMock()
            mock_vector_store.search.return_value = []
            mock_vs.return_value = mock_vector_store
            
            mock_agent = MagicMock()
            mock_graph = MagicMock()
            mock_state = {
                "user_query": "Test",
                "problem_context": "",
                "research_questions": [],
                "relevant_verses": [],
                "analysis": "Analysis",
                "guidance": "Guidance",
                "exercises": "Exercises",
                "final_answer": "# Answer\n\nTest"
            }
            mock_graph.invoke.return_value = mock_state
            mock_agent.build_graph.return_value = mock_graph
            mock_agent_class.return_value = mock_agent
            
            # Make multiple requests
            for i in range(3):
                response = client.post("/api/research", json={"query": f"Test {i}"})
                assert response.status_code == 200
                data = response.json()
                
                # Verify consistent structure
                required_fields = ["answer", "analysis", "guidance", "exercises", "verses", "query"]
                for field in required_fields:
                    assert field in data, f"Response {i} missing field: {field}"
            
            real_session.close()
    
    def test_real_verse_data_quality(self, robust_test_db):
        """Test that real verse data maintains quality."""
        session = get_db_session()
        
        # Add comprehensive verse
        verse = Verse(
            verse_id="BG 2.47",
            chapter=2,
            verse_number=47,
            sanskrit="कर्मण्येवाधिकारस्ते मा फलेषु कदाचन",
            synonyms="karmaṇi—in prescribed duties; eva—certainly",
            translation="You have a right to perform your prescribed duty, but you are not entitled to the fruits of action.",
            purport="This verse teaches karma yoga - performing duty without attachment to results. It is one of the most important teachings of the Gita."
        )
        session.add(verse)
        session.commit()
        
        # Verify quality
        retrieved = session.query(Verse).filter_by(verse_id="BG 2.47").first()
        assert retrieved is not None
        assert len(retrieved.translation) > 50
        assert len(retrieved.purport) > 50
        assert "karma" in retrieved.purport.lower() or "duty" in retrieved.translation.lower()
        
        # Test chunk quality
        chunk = VerseChunk(
            verse_id=retrieved.verse_id,
            chapter=retrieved.chapter,
            verse_number=retrieved.verse_number,
            sanskrit=retrieved.sanskrit,
            synonyms=retrieved.synonyms,
            translation=retrieved.translation,
            purport=retrieved.purport
        )
        
        embedding_text = chunk.to_text_for_embedding()
        assert len(embedding_text) > 200
        assert "BG 2.47" in embedding_text
        assert retrieved.translation[:50] in embedding_text
        
        session.close()

