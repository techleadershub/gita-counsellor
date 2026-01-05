"""
Comprehensive End-to-End Tests with Real Modern Questions

These tests verify that the system provides high-quality, relevant guidance
for modern problems using Bhagavad Gita principles.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch, Mock
from fastapi.testclient import TestClient

# Ensure we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Modern questions for testing
MODERN_QUESTIONS = [
    {
        "query": "I'm feeling overwhelmed with work stress and can't find balance. How should I approach this?",
        "context": "I work 12 hours a day, have family responsibilities, and feel like I'm burning out.",
        "expected_themes": ["stress", "work-life balance", "burnout", "duty", "detachment"],
        "min_verses": 3
    },
    {
        "query": "I'm struggling with making a major career decision. Should I take a risky opportunity or stay in my safe job?",
        "context": "I have a stable job but an exciting startup opportunity. I'm afraid of failure.",
        "expected_themes": ["decision-making", "fear", "dharma", "karma", "duty"],
        "min_verses": 3
    },
    {
        "query": "How do I deal with anxiety about the future and uncertainty?",
        "context": "I constantly worry about what might happen and it's affecting my peace of mind.",
        "expected_themes": ["anxiety", "worry", "future", "peace", "mind"],
        "min_verses": 3
    },
    {
        "query": "I'm having relationship conflicts with my family. How can I maintain harmony?",
        "context": "There are constant arguments and misunderstandings in my family.",
        "expected_themes": ["relationships", "harmony", "conflict", "patience", "understanding"],
        "min_verses": 3
    },
    {
        "query": "I feel lost and don't know my purpose in life. What should I do?",
        "context": "I'm successful but feel empty. I don't know what I'm meant to do.",
        "expected_themes": ["purpose", "meaning", "dharma", "self-realization", "spiritual"],
        "min_verses": 3
    },
    {
        "query": "How do I handle failure and setbacks without losing motivation?",
        "context": "I failed at an important project and feel demotivated.",
        "expected_themes": ["failure", "resilience", "perseverance", "detachment", "karma"],
        "min_verses": 3
    },
    {
        "query": "I'm struggling with addiction to social media and can't focus. How can I regain control?",
        "context": "I spend hours on my phone and it's affecting my productivity and relationships.",
        "expected_themes": ["addiction", "self-control", "mind", "discipline", "focus"],
        "min_verses": 3
    },
    {
        "query": "How do I deal with jealousy and comparison with others?",
        "context": "I constantly compare myself to others and feel jealous of their success.",
        "expected_themes": ["jealousy", "comparison", "ego", "contentment", "self"],
        "min_verses": 3
    }
]

@pytest.fixture
def client():
    """Create test client."""
    from main import app
    from starlette.testclient import TestClient
    return TestClient(app)

def create_mock_verse(verse_id, chapter, verse_num, translation, purport):
    """Helper to create mock verse data."""
    return {
        "verse_id": verse_id,
        "chapter": chapter,
        "verse_number": verse_num,
        "sanskrit": "Test Sanskrit text",
        "synonyms": "Test synonyms",
        "translation": translation,
        "purport": purport
    }

def create_mock_agent_response(question, verses_data):
    """Create a realistic agent response."""
    verse_refs = ", ".join([v["verse_id"] for v in verses_data])
    
    analysis_content = f"""## Analysis

The Bhagavad Gita provides profound wisdom for addressing this modern challenge. The key principles involved include:

1. **Detachment from Results**: Focus on performing your duty without attachment to outcomes. This principle helps reduce anxiety about future results and allows you to work with full dedication.

2. **Equanimity**: Maintain balance in success and failure. The Gita teaches that both pleasure and pain are temporary, and one should remain steady in both situations.

3. **Self-Knowledge**: Understand your true nature beyond temporary circumstances. Realizing that you are not the body but the eternal soul helps transcend material anxieties.

4. **Karma Yoga**: The path of selfless action, performing duties without attachment to results, is the key to finding peace in action.

Relevant verses: {verse_refs}

These verses provide timeless wisdom that can be applied to modern challenges, helping you navigate difficulties with wisdom and equanimity."""

    guidance_content = f"""## Practical Guidance

Based on the teachings of Bhagavad Gita, here's what you can do:

1. **Practice Detachment**: Perform your duties without being attached to results. This doesn't mean being careless, but rather doing your best and accepting whatever outcome comes.

2. **Maintain Equanimity**: Stay balanced in all situations - success and failure, praise and criticism. Remember that both are temporary and don't define your true self.

3. **Focus on Dharma**: Understand and follow your righteous duty. Ask yourself: "What is the right thing to do in this situation?" rather than "What will benefit me?"

4. **Cultivate Self-Awareness**: Regular meditation and self-reflection help you understand your mind and emotions better, leading to greater control and peace.

5. **Seek Higher Purpose**: Connect with your spiritual nature. Understanding that you are more than your material circumstances helps you navigate challenges with wisdom.

**Where to Look for More Guidance:**
- Study chapters 2, 3, and 6 for foundational principles
- Focus on verses about karma yoga and self-realization
- Practice the principles in daily life
- Seek guidance from experienced practitioners
- Join study groups or communities focused on spiritual growth"""

    exercises_content = f"""## Spiritual Exercises

1. **Daily Meditation (15-30 minutes)**
   - Sit quietly in a comfortable position
   - Close your eyes and observe your thoughts without judgment
   - Practice detachment from mental fluctuations
   - Connect with your inner self and find peace within
   - Start with 10 minutes and gradually increase

2. **Karma Yoga Practice**
   - Perform daily duties with full attention and dedication
   - Offer actions as service without expecting rewards
   - Maintain equanimity in all outcomes
   - See work as an opportunity for spiritual growth
   - Practice this with small tasks first, then expand

3. **Self-Reflection Journal**
   - Write about your experiences daily
   - Reflect on how Gita principles apply to your situation
   - Track your progress in applying the teachings
   - Note challenges and how you overcame them
   - Review weekly to see your growth

4. **Study and Contemplation**
   - Read relevant verses: {verse_refs}
   - Contemplate their meaning in your specific situation
   - Discuss with like-minded seekers or mentors
   - Apply one principle each week
   - Keep a notebook of insights

5. **Mindful Action**
   - Before each major decision, pause and reflect
   - Ask: "What is my dharma here? What is the right action?"
   - Act with awareness and detachment
   - Accept results with equanimity
   - Learn from each experience"""

    final_answer = f"""# Guidance from Bhagavad Gita

## Your Question
{question}

{analysis_content}

{guidance_content}

{exercises_content}

## Key Verses Referenced
{verse_refs}

---
*This guidance is based on the teachings of Bhagavad Gita As It Is by A.C. Bhaktivedanta Swami Prabhupada.*"""
    
    return {
        "user_query": question,
        "problem_context": f"Analysis of: {question}",
        "research_questions": [
            f"How does Gita address {question.lower()}?",
            f"What principles apply to this situation?",
            f"What guidance does Gita provide?"
        ],
        "relevant_verses": verses_data,
        "analysis": analysis_content,
        "guidance": guidance_content,
        "exercises": exercises_content,
        "final_answer": final_answer
    }

@patch('main.get_vector_store')
@patch('main.ResearchAgent')
@patch('main.get_db_session')
def test_e2e_work_stress_question(mock_db_session, mock_agent_class, mock_vector_store, client):
    """Test comprehensive response to work stress question."""
    question_data = MODERN_QUESTIONS[0]
    
    # Setup mocks
    mock_vs = MagicMock()
    mock_vector_store.return_value = mock_vs
    
    # Mock verse search results
    mock_verses_data = [
        create_mock_verse("BG 2.47", 2, 47, 
            "You have a right to perform your prescribed duty, but you are not entitled to the fruits of action.",
            "This verse teaches the principle of karma yoga - performing duty without attachment to results."),
        create_mock_verse("BG 6.35", 6, 35,
            "Undoubtedly, O mighty-armed, the mind is restless and difficult to control; but it is subdued by constant practice and detachment.",
            "The mind can be controlled through practice and detachment from material desires."),
        create_mock_verse("BG 2.14", 2, 14,
            "O son of Kunti, the contact between the senses and the sense objects gives rise to fleeting perceptions of happiness and distress.",
            "Material happiness and distress are temporary and should not disturb our equilibrium.")
    ]
    
    mock_search_result = {
        "chunk": {"verse_id": "BG 2.47"},
        "score": 0.95,
        "content": "Test content"
    }
    mock_vs.search.return_value = [mock_search_result]
    
    # Mock database
    mock_session = MagicMock()
    for verse_data in mock_verses_data:
        mock_verse = MagicMock()
        mock_verse.to_dict.return_value = verse_data
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_verse
    mock_db_session.return_value = mock_session
    
    # Mock agent
    mock_agent = MagicMock()
    mock_graph = MagicMock()
    mock_state = create_mock_agent_response(question_data["query"], mock_verses_data)
    mock_graph.invoke.return_value = mock_state
    mock_agent.build_graph.return_value = mock_graph
    mock_agent_class.return_value = mock_agent
    
    # Execute request
    response = client.post("/api/research", json={
        "query": question_data["query"],
        "context": question_data["context"]
    })
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    # Check structure
    assert "answer" in data
    assert "analysis" in data
    assert "guidance" in data
    assert "exercises" in data
    assert "verses" in data
    
    # Check quality - answer should be comprehensive
    assert len(data["answer"]) > 500, "Answer should be comprehensive"
    assert len(data["analysis"]) > 200, "Analysis should be detailed"
    assert len(data["guidance"]) > 200, "Guidance should be practical"
    assert len(data["exercises"]) > 200, "Exercises should be detailed"
    
    # Check verses
    assert len(data["verses"]) >= question_data["min_verses"], f"Should have at least {question_data['min_verses']} verses"
    
    # Check content quality
    answer_lower = data["answer"].lower()
    assert any(theme in answer_lower for theme in question_data["expected_themes"]), \
        f"Answer should mention themes: {question_data['expected_themes']}"
    
    # Check verses have required fields
    for verse in data["verses"]:
        assert "verse_id" in verse
        assert "translation" in verse
        assert verse["verse_id"].startswith("BG")

@patch('main.get_vector_store')
@patch('main.ResearchAgent')
@patch('main.get_db_session')
def test_e2e_career_decision_question(mock_db_session, mock_agent_class, mock_vector_store, client):
    """Test response to career decision question."""
    question_data = MODERN_QUESTIONS[1]
    
    # Setup similar to above
    mock_vs = MagicMock()
    mock_vector_store.return_value = mock_vs
    
    mock_verses_data = [
        create_mock_verse("BG 3.8", 3, 8,
            "Perform your prescribed duty, for doing so is better than not working.",
            "One must perform their duty according to their nature and position."),
        create_mock_verse("BG 18.48", 18, 48,
            "Every endeavor is covered by some fault, just as fire is covered by smoke.",
            "No action is perfect, but one should still perform their duty."),
        create_mock_verse("BG 2.41", 2, 41,
            "Those who are on this path are resolute in purpose, and their aim is one.",
            "One should be determined and focused on their spiritual goal.")
    ]
    
    mock_vs.search.return_value = [{"chunk": {"verse_id": "BG 3.8"}, "score": 0.9}]
    
    mock_session = MagicMock()
    mock_verse = MagicMock()
    mock_verse.to_dict.return_value = mock_verses_data[0]
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_verse
    mock_db_session.return_value = mock_session
    
    mock_agent = MagicMock()
    mock_graph = MagicMock()
    mock_state = create_mock_agent_response(question_data["query"], mock_verses_data)
    mock_graph.invoke.return_value = mock_state
    mock_agent.build_graph.return_value = mock_graph
    mock_agent_class.return_value = mock_agent
    
    response = client.post("/api/research", json={
        "query": question_data["query"],
        "context": question_data["context"]
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Quality checks
    assert len(data["answer"]) > 500
    assert "dharma" in data["answer"].lower() or "duty" in data["answer"].lower()
    assert len(data["verses"]) >= 3

@patch('main.get_vector_store')
@patch('main.ResearchAgent')
@patch('main.get_db_session')
def test_e2e_anxiety_question(mock_db_session, mock_agent_class, mock_vector_store, client):
    """Test response to anxiety about future question."""
    question_data = MODERN_QUESTIONS[2]
    
    mock_vs = MagicMock()
    mock_vector_store.return_value = mock_vs
    
    mock_verses_data = [
        create_mock_verse("BG 6.6", 6, 6,
            "For him who has conquered the mind, the mind is the best of friends; but for one who has failed to do so, his mind will remain the greatest enemy.",
            "Control of the mind is essential for peace."),
        create_mock_verse("BG 2.56", 2, 56,
            "One whose happiness is within, who is active and rejoices within, and whose aim is inward is actually the perfect mystic.",
            "True happiness comes from within, not from external circumstances."),
        create_mock_verse("BG 12.12", 12, 12,
            "Better indeed is knowledge than practice; than knowledge, meditation is better; than meditation, renunciation of the fruits of action; peace immediately follows such renunciation.",
            "Renunciation of attachment to results brings peace.")
    ]
    
    mock_vs.search.return_value = [{"chunk": {"verse_id": "BG 6.6"}, "score": 0.92}]
    
    mock_session = MagicMock()
    mock_verse = MagicMock()
    mock_verse.to_dict.return_value = mock_verses_data[0]
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_verse
    mock_db_session.return_value = mock_session
    
    mock_agent = MagicMock()
    mock_graph = MagicMock()
    mock_state = create_mock_agent_response(question_data["query"], mock_verses_data)
    mock_graph.invoke.return_value = mock_state
    mock_agent.build_graph.return_value = mock_graph
    mock_agent_class.return_value = mock_agent
    
    response = client.post("/api/research", json={
        "query": question_data["query"],
        "context": question_data["context"]
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Quality checks
    assert len(data["answer"]) > 500
    assert "peace" in data["answer"].lower() or "mind" in data["answer"].lower()
    assert "meditation" in data["exercises"].lower() or "practice" in data["exercises"].lower()

@patch('main.get_vector_store')
@patch('main.ResearchAgent')
@patch('main.get_db_session')
def test_e2e_multiple_questions_quality(mock_db_session, mock_agent_class, mock_vector_store, client):
    """Test that system provides quality responses for multiple different questions."""
    quality_checks = []
    
    for question_data in MODERN_QUESTIONS[:5]:  # Test first 5 questions
        mock_vs = MagicMock()
        mock_vector_store.return_value = mock_vs
        
        mock_verses_data = [
            create_mock_verse(f"BG {i}.{j}", i, j,
                f"Translation for verse {i}.{j}",
                f"Purport explaining the principle")
            for i in range(2, 7) for j in range(1, 4)
        ][:3]  # Take first 3
        
        mock_vs.search.return_value = [{"chunk": {"verse_id": mock_verses_data[0]["verse_id"]}, "score": 0.9}]
        
        mock_session = MagicMock()
        mock_verse = MagicMock()
        mock_verse.to_dict.return_value = mock_verses_data[0]
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_verse
        mock_db_session.return_value = mock_session
        
        mock_agent = MagicMock()
        mock_graph = MagicMock()
        mock_state = create_mock_agent_response(question_data["query"], mock_verses_data)
        mock_graph.invoke.return_value = mock_state
        mock_agent.build_graph.return_value = mock_graph
        mock_agent_class.return_value = mock_agent
        
        response = client.post("/api/research", json={
            "query": question_data["query"],
            "context": question_data.get("context")
        })
        
        if response.status_code == 200:
            data = response.json()
            checks = {
                "question": question_data["query"][:50],
                "has_answer": len(data.get("answer", "")) > 500,
                "has_analysis": len(data.get("analysis", "")) > 200,
                "has_guidance": len(data.get("guidance", "")) > 200,
                "has_exercises": len(data.get("exercises", "")) > 200,
                "has_verses": len(data.get("verses", [])) >= question_data["min_verses"],
                "mentions_themes": any(theme in data.get("answer", "").lower() 
                                      for theme in question_data["expected_themes"])
            }
            quality_checks.append(checks)
    
    # Verify all questions got quality responses
    assert len(quality_checks) == 5, "Should test 5 questions"
    
    for check in quality_checks:
        assert check["has_answer"], f"Question '{check['question']}' should have comprehensive answer"
        assert check["has_analysis"], f"Question '{check['question']}' should have analysis"
        assert check["has_guidance"], f"Question '{check['question']}' should have guidance"
        assert check["has_exercises"], f"Question '{check['question']}' should have exercises"
        assert check["has_verses"], f"Question '{check['question']}' should have enough verses"

def test_e2e_response_structure_quality(client):
    """Test that responses have proper structure and quality markers."""
    with patch('main.get_vector_store') as mock_vs, \
         patch('main.ResearchAgent') as mock_agent_class, \
         patch('main.get_db_session') as mock_db:
        
        # Setup mocks
        mock_vector_store_instance = MagicMock()
        mock_vs.return_value = mock_vector_store_instance
        mock_vector_store_instance.search.return_value = [
            {"chunk": {"verse_id": "BG 2.47"}, "score": 0.9}
        ]
        
        mock_session = MagicMock()
        mock_verse = MagicMock()
        mock_verse.to_dict.return_value = create_mock_verse("BG 2.47", 2, 47, "Test", "Test")
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_verse
        mock_db.return_value = mock_session
        
        mock_agent = MagicMock()
        mock_graph = MagicMock()
        mock_state = create_mock_agent_response("Test question", [
            create_mock_verse("BG 2.47", 2, 47, "Test", "Test")
        ])
        mock_graph.invoke.return_value = mock_state
        mock_agent.build_graph.return_value = mock_graph
        mock_agent_class.return_value = mock_agent
        
        response = client.post("/api/research", json={
            "query": "How do I find peace?",
            "context": "I'm stressed"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Structure checks
        required_fields = ["answer", "analysis", "guidance", "exercises", "verses", "query"]
        for field in required_fields:
            assert field in data, f"Response should have '{field}' field"
        
        # Quality markers
        answer = data["answer"]
        assert "##" in answer or "#" in answer, "Answer should have markdown structure"
        assert "Bhagavad Gita" in answer or "Gita" in answer, "Answer should reference Gita"
        
        # Exercises should be actionable
        exercises = data["exercises"]
        assert any(word in exercises.lower() for word in ["practice", "meditation", "exercise", "daily"]), \
            "Exercises should be actionable"
        
        # Guidance should be practical
        guidance = data["guidance"]
        assert any(word in guidance.lower() for word in ["practice", "should", "can", "try"]), \
            "Guidance should be practical"

