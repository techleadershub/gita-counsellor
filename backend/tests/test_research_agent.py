import pytest
from unittest.mock import MagicMock, patch
from research_agent import ResearchAgent, AgentState

def test_research_agent_initialization(mock_research_agent):
    """Test research agent initialization."""
    assert mock_research_agent is not None
    assert mock_research_agent.vector_store is not None
    assert mock_research_agent.llm is not None

def test_analyze_problem_node(mock_research_agent):
    """Test problem analysis node."""
    state = {
        "user_query": "I'm stressed about my career",
        "problem_context": "",
        "research_questions": [],
        "relevant_verses": [],
        "analysis": "",
        "guidance": "",
        "exercises": "",
        "final_answer": ""
    }
    
    # Mock LLM response
    mock_response = MagicMock()
    mock_response.content = "CORE_ISSUE: Career stress\nKEY_THEMES: stress, career, purpose\nRELEVANT_PRINCIPLES: karma, dharma"
    mock_research_agent.llm.invoke.return_value = mock_response
    
    result = mock_research_agent.analyze_problem_node(state)
    
    assert "problem_context" in result
    assert "research_questions" in result
    assert len(result["research_questions"]) > 0

def test_research_verses_node(mock_research_agent, mock_db_session):
    """Test verse research node."""
    state = {
        "user_query": "Test query",
        "problem_context": "",
        "research_questions": ["How to deal with stress?"],
        "relevant_verses": [],
        "analysis": "",
        "guidance": "",
        "exercises": "",
        "final_answer": ""
    }
    
    # Mock vector store search
    mock_result = {
        "chunk": {"verse_id": "BG 2.12"},
        "score": 0.9
    }
    mock_research_agent.vector_store.search.return_value = [mock_result]
    
    # Mock database query
    with patch('research_agent.get_db_session') as mock_db:
        mock_verse = MagicMock()
        mock_verse.to_dict.return_value = {
            "verse_id": "BG 2.12",
            "chapter": 2,
            "verse_number": 12,
            "translation": "Test translation"
        }
        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_verse
        mock_db.return_value = mock_session
        
        result = mock_research_agent.research_verses_node(state)
        
        assert "relevant_verses" in result
        assert len(result["relevant_verses"]) > 0

def test_synthesize_guidance_node(mock_research_agent):
    """Test guidance synthesis node."""
    state = {
        "user_query": "How to deal with stress?",
        "problem_context": "Analysis of stress",
        "research_questions": [],
        "relevant_verses": [{
            "verse_id": "BG 2.12",
            "chapter": 2,
            "verse_number": 12,
            "translation": "Test translation",
            "purport": "Test purport"
        }],
        "analysis": "",
        "guidance": "",
        "exercises": "",
        "final_answer": ""
    }
    
    # Mock LLM response with sections
    mock_response = MagicMock()
    mock_response.content = """
ANALYSIS: This is the analysis section.

PRACTICAL GUIDANCE: This is the guidance section.

SPIRITUAL EXERCISES: This is the exercises section.
"""
    mock_research_agent.llm.invoke.return_value = mock_response
    
    result = mock_research_agent.synthesize_guidance_node(state)
    
    assert "analysis" in result
    assert "guidance" in result
    assert "exercises" in result

def test_finalize_answer_node(mock_research_agent):
    """Test final answer node."""
    state = {
        "user_query": "Test question",
        "problem_context": "",
        "research_questions": [],
        "relevant_verses": [{"verse_id": "BG 2.12"}],
        "analysis": "Test analysis",
        "guidance": "Test guidance",
        "exercises": "Test exercises",
        "final_answer": ""
    }
    
    result = mock_research_agent.finalize_answer_node(state)
    
    assert "final_answer" in result
    assert "Test question" in result["final_answer"]
    assert "BG 2.12" in result["final_answer"]

def test_build_graph(mock_research_agent):
    """Test graph construction."""
    graph = mock_research_agent.build_graph()
    
    assert graph is not None
    # Graph should be compilable
    assert hasattr(graph, 'invoke')

def test_log_callback(mock_research_agent):
    """Test logging callback."""
    log_messages = []
    
    def log_callback(msg):
        log_messages.append(msg)
    
    mock_research_agent.log_callback = log_callback
    mock_research_agent.log("Test message")
    
    assert "Test message" in log_messages

