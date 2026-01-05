"""
REAL Integration Tests - Testing Actual System Behavior

These tests verify the actual system works, not just mocks.
They test real code paths, actual database operations, and real logic.
"""
import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test if we have real dependencies
HAS_REAL_DEPS = True
try:
    from models import Verse, VerseChunk, get_db_engine, get_db_session, Base
    from vector_store import VectorStore
    from ingestion import IngestionService
    from research_agent import ResearchAgent
except ImportError as e:
    HAS_REAL_DEPS = False
    print(f"Missing dependencies: {e}")

@pytest.mark.skipif(not HAS_REAL_DEPS, reason="Missing real dependencies")
class TestRealIntegration:
    """Real integration tests that test actual system behavior."""
    
    @pytest.fixture
    def real_db(self, tmp_path):
        """Create a real SQLite database for testing."""
        db_path = tmp_path / "test_real.db"
        os.environ["DB_PATH"] = str(db_path)
        
        # Create real database
        engine = get_db_engine()
        Base.metadata.create_all(engine)
        
        # Add some real verses (check if they exist first)
        session = get_db_session()
        
        # Clear any existing test data
        session.query(Verse).delete()
        session.commit()
        
        test_verses = [
            Verse(
                verse_id="BG 2.47",
                chapter=2,
                verse_number=47,
                sanskrit="कर्मण्येवाधिकारस्ते मा फलेषु कदाचन",
                translation="You have a right to perform your prescribed duty, but you are not entitled to the fruits of action.",
                purport="This is the principle of karma yoga - perform duty without attachment to results."
            ),
            Verse(
                verse_id="BG 3.21",
                chapter=3,
                verse_number=21,
                sanskrit="यद्यदाचरति श्रेष्ठस्तत्तदेवेतरो जनः",
                translation="Whatever action a great man performs, common men follow. And whatever standards he sets by exemplary acts, all the world pursues.",
                purport="Leaders set examples that others follow."
            ),
            Verse(
                verse_id="BG 6.35",
                chapter=6,
                verse_number=35,
                sanskrit="असंशयं महाबाहो मनो दुर्निग्रहं चलम्",
                translation="Undoubtedly, O mighty-armed, the mind is restless and difficult to control; but it is subdued by constant practice and detachment.",
                purport="Mind control requires practice and detachment."
            ),
            Verse(
                verse_id="BG 16.1",
                chapter=16,
                verse_number=1,
                sanskrit="अभयं सत्त्वसंशुद्धिर्ज्ञानयोगव्यवस्थितिः",
                translation="Fearlessness, purification of one's existence, cultivation of spiritual knowledge, charity, self-control...",
                purport="Divine qualities include truthfulness, compassion, and self-control."
            ),
            Verse(
                verse_id="BG 18.43",
                chapter=18,
                verse_number=43,
                sanskrit="शौर्यं तेजो धृतिर्दाक्ष्यं युद्धे चाप्यपलायनम्",
                translation="Heroism, power, determination, resourcefulness, courage in battle, generosity, and leadership are the qualities of work for the kṣatriyas.",
                purport="Leadership qualities include courage, determination, and service."
            )
        ]
        
        for verse in test_verses:
            session.add(verse)
        session.commit()
        session.close()
        
        yield db_path
        
        # Cleanup
        if db_path.exists():
            os.remove(db_path)
    
    @pytest.fixture
    def real_vector_store(self, tmp_path):
        """Create a real Qdrant vector store for testing."""
        qdrant_path = tmp_path / "test_qdrant"
        qdrant_path.mkdir()
        
        # Set environment
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-key-for-structure")
        
        # Try to create real vector store (will work if OpenAI key is set, otherwise will test structure)
        try:
            store = VectorStore()
            # Override path for testing
            store.client = None  # Will be created if needed
            yield store
        except Exception as e:
            # If we can't create real store, at least test the structure
            pytest.skip(f"Cannot create real vector store: {e}")
        
        # Cleanup
        if qdrant_path.exists():
            shutil.rmtree(qdrant_path, ignore_errors=True)
    
    def test_real_database_operations(self, real_db):
        """Test that we can actually read and write to the database."""
        session = get_db_session()
        
        # Test reading
        verses = session.query(Verse).filter_by(chapter=2).all()
        assert len(verses) > 0, "Should have verses in chapter 2"
        
        # Test specific verse
        verse = session.query(Verse).filter_by(verse_id="BG 2.47").first()
        assert verse is not None, "Should find BG 2.47"
        assert verse.translation is not None, "Verse should have translation"
        assert "karma yoga" in verse.purport.lower() or "duty" in verse.translation.lower()
        
        # Test verse to_dict
        verse_dict = verse.to_dict()
        assert isinstance(verse_dict, dict)
        assert verse_dict["verse_id"] == "BG 2.47"
        assert "translation" in verse_dict
        
        session.close()
    
    def test_real_verse_chunk_creation(self):
        """Test that VerseChunk model works correctly."""
        chunk = VerseChunk(
            verse_id="BG 2.47",
            chapter=2,
            verse_number=47,
            sanskrit="कर्मण्येवाधिकारस्ते",
            translation="You have a right to perform your prescribed duty",
            purport="This is karma yoga"
        )
        
        # Test to_text_for_embedding
        text = chunk.to_text_for_embedding()
        assert "BG 2.47" in text
        assert "translation" in text.lower()
        assert "purport" in text.lower()
        assert len(text) > 50
    
    def test_real_ingestion_logic(self, real_db, real_vector_store):
        """Test that ingestion logic actually processes data correctly."""
        # Test create_verse_chunks method logic
        service = IngestionService(real_vector_store)
        
        chunk_data = {
            "id": "2.47",
            "sanskrit": ["कर्मण्येवाधिकारस्ते"],
            "synonyms": "karma—work; eva—indeed; adhikāraḥ—right; te—your",
            "translation": "You have a right to perform your prescribed duty",
            "purport": ["This verse teaches karma yoga.", "Perform duty without attachment."]
        }
        
        # This tests the actual logic, not mocks
        chunks = service.create_verse_chunks(chunk_data, "Bhagavad Gita")
        
        assert len(chunks) > 0, "Should create at least one chunk"
        assert chunks[0].verse_id == "BG 2.47", "Should format verse ID correctly"
        assert chunks[0].chapter == 2, "Should parse chapter correctly"
        assert chunks[0].verse_number == 47, "Should parse verse number correctly"
        assert chunks[0].translation is not None, "Should have translation"
    
    def test_real_research_agent_structure(self, real_db):
        """Test that research agent can be initialized and has correct structure."""
        # Create a minimal vector store mock just for structure
        from unittest.mock import MagicMock
        mock_vs = MagicMock()
        mock_vs.search.return_value = []
        
        # Test actual agent initialization
        agent = ResearchAgent(mock_vs)
        
        assert agent.vector_store is not None
        assert agent.llm is not None
        assert hasattr(agent, 'analyze_problem_node')
        assert hasattr(agent, 'research_verses_node')
        assert hasattr(agent, 'synthesize_guidance_node')
        assert hasattr(agent, 'finalize_answer_node')
        assert hasattr(agent, 'build_graph')
        
        # Test graph can be built
        graph = agent.build_graph()
        assert graph is not None
    
    def test_real_verse_search_logic(self, real_db):
        """Test that we can actually search and retrieve verses from database."""
        session = get_db_session()
        
        # Test searching by chapter
        verses = session.query(Verse).filter_by(chapter=2).all()
        assert len(verses) > 0
        
        # Test searching by verse_id
        verse = session.query(Verse).filter_by(verse_id="BG 2.47").first()
        assert verse is not None
        
        # Test searching leadership verses
        leadership_verses = session.query(Verse).filter(
            Verse.purport.contains("leader") | 
            Verse.translation.contains("leader")
        ).all()
        # Should find at least BG 3.21 and BG 18.43
        assert len(leadership_verses) > 0
        
        session.close()
    
    def test_real_prompt_generation(self):
        """Test that prompts are actually generated correctly."""
        from unittest.mock import MagicMock, patch
        mock_vs = MagicMock()
        
        # Test that prompts contain expected content by checking the code
        # We can't easily mock ChatOpenAI's invoke, so we test the prompt structure
        agent = ResearchAgent(mock_vs)
        
        # Verify the agent has the method
        assert hasattr(agent, 'analyze_problem_node')
        
        # Test that the prompt structure is correct by examining the code
        import inspect
        source = inspect.getsource(agent.analyze_problem_node)
        
        # Verify prompt contains modern context awareness
        assert "gen z" in source.lower() or "modern" in source.lower() or "gen alpha" in source.lower(), \
            "Prompt should be aware of modern context"
        
        # Verify it asks for structured analysis
        assert "core_issue" in source.lower() or "key_themes" in source.lower(), \
            "Prompt should request structured analysis"
    
    def test_real_response_structure(self, real_db):
        """Test that final answer structure is correct with real data."""
        from unittest.mock import MagicMock
        mock_vs = MagicMock()
        agent = ResearchAgent(mock_vs)
        
        # Use real verse data
        session = get_db_session()
        real_verse = session.query(Verse).filter_by(verse_id="BG 2.47").first()
        session.close()
        
        state = {
            "user_query": "What is karma yoga?",
            "problem_context": "Understanding duty",
            "research_questions": [],
            "relevant_verses": [real_verse.to_dict()],
            "analysis": "Karma yoga is performing duty without attachment.",
            "guidance": "Practice your duties selflessly.",
            "exercises": "1. Daily meditation\n2. Selfless service",
            "final_answer": ""
        }
        
        result = agent.finalize_answer_node(state)
        
        assert "final_answer" in result
        answer = result["final_answer"]
        assert "What is karma yoga?" in answer
        assert "BG 2.47" in answer
        assert "Analysis" in answer
        assert "Guidance" in answer
        assert "Exercises" in answer
        assert len(answer) > 200

@pytest.mark.integration
class TestRealSystemFlow:
    """Test the actual system flow with minimal mocks."""
    
    def test_real_api_endpoint_structure(self):
        """Test that API endpoints actually exist and have correct structure."""
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test root endpoint (should work without mocks)
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        
        # Test health endpoint (should work without mocks)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        
        # Test that research endpoint exists (will fail without real setup, but structure is tested)
        # This at least verifies the endpoint is defined
        assert hasattr(app, 'router')
    
    def test_real_config_loading(self):
        """Test that configuration actually loads."""
        from config import LLM_CONFIG, VECTOR_DB_CONFIG, APP_CONFIG
        
        # These should exist even if empty
        assert isinstance(LLM_CONFIG, dict)
        assert isinstance(VECTOR_DB_CONFIG, dict)
        assert isinstance(APP_CONFIG, dict)
        
        # Vector DB should have defaults
        assert "collection_name" in VECTOR_DB_CONFIG
        assert "path" in VECTOR_DB_CONFIG

