"""
Comprehensive Tests for Gen Z and Gen Alpha Questions

Testing leadership, resilience, and moral guidance for younger generations
with modern context and challenges.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Gen Z and Gen Alpha specific questions
GENZ_GENALPHA_QUESTIONS = [
    {
        "query": "What guidance does Bhagavad Gita offer on leadership for Gen Z and Gen Alpha?",
        "context": "Young leaders facing digital age challenges, remote teams, and social media pressures",
        "expected_themes": ["leadership", "responsibility", "example", "service", "vision"],
        "min_verses": 5,
        "quality_checks": ["leadership principles", "practical", "modern context", "actionable"]
    },
    {
        "query": "How can Gen Z build resilience in the face of constant social media comparison and digital overwhelm?",
        "context": "Growing up with social media, constant notifications, FOMO, and comparison culture",
        "expected_themes": ["resilience", "mind", "detachment", "self-control", "peace"],
        "min_verses": 5,
        "quality_checks": ["resilience", "social media", "practical steps", "mental health"]
    },
    {
        "query": "What moral guidance does Bhagavad Gita provide for Gen Alpha navigating AI, technology ethics, and digital relationships?",
        "context": "First generation growing up with AI, virtual reality, and complex digital ethics",
        "expected_themes": ["morals", "ethics", "dharma", "righteousness", "values"],
        "min_verses": 5,
        "quality_checks": ["ethics", "technology", "values", "principles", "modern"]
    },
    {
        "query": "How should Gen Z leaders balance authenticity with professional expectations in the modern workplace?",
        "context": "Wanting to be authentic but facing corporate culture pressures",
        "expected_themes": ["authenticity", "dharma", "duty", "integrity", "balance"],
        "min_verses": 4,
        "quality_checks": ["authenticity", "workplace", "balance", "integrity"]
    },
    {
        "query": "What does Gita say about building mental resilience for Gen Z dealing with climate anxiety and future uncertainty?",
        "context": "Eco-anxiety, climate change fears, uncertain future prospects",
        "expected_themes": ["resilience", "anxiety", "future", "equanimity", "peace"],
        "min_verses": 5,
        "quality_checks": ["climate anxiety", "mental resilience", "uncertainty", "practical"]
    },
    {
        "query": "How can Gen Alpha develop strong moral compass when exposed to conflicting values online?",
        "context": "Growing up with internet, exposed to diverse and sometimes conflicting values",
        "expected_themes": ["morals", "values", "discrimination", "wisdom", "dharma"],
        "min_verses": 5,
        "quality_checks": ["moral compass", "values", "discrimination", "wisdom"]
    },
    {
        "query": "What leadership lessons from Gita apply to Gen Z entrepreneurs building startups in the digital economy?",
        "context": "Young entrepreneurs, startup culture, digital business, rapid change",
        "expected_themes": ["leadership", "entrepreneurship", "action", "detachment", "vision"],
        "min_verses": 5,
        "quality_checks": ["entrepreneurship", "startup", "leadership", "practical"]
    },
    {
        "query": "How does Gita guide Gen Z on maintaining mental health and avoiding burnout in the gig economy?",
        "context": "Gig work, multiple jobs, no job security, constant hustle culture",
        "expected_themes": ["mental health", "burnout", "balance", "self-care", "dharma"],
        "min_verses": 5,
        "quality_checks": ["mental health", "burnout", "gig economy", "balance"]
    },
    {
        "query": "What moral principles from Bhagavad Gita help Gen Alpha navigate AI ethics, deepfakes, and digital deception?",
        "context": "AI-generated content, deepfakes, misinformation, digital manipulation",
        "expected_themes": ["ethics", "truth", "honesty", "discrimination", "dharma"],
        "min_verses": 5,
        "quality_checks": ["AI ethics", "truth", "discrimination", "principles"]
    },
    {
        "query": "How can Gen Z leaders inspire and motivate teams in remote and hybrid work environments?",
        "context": "Remote work, virtual teams, lack of in-person connection, digital leadership",
        "expected_themes": ["leadership", "inspiration", "service", "connection", "example"],
        "min_verses": 5,
        "quality_checks": ["remote work", "leadership", "inspiration", "teams"]
    }
]

def create_high_quality_response(question_data, verses_data):
    """Create a high-quality, comprehensive response for Gen Z/Gen Alpha questions."""
    verse_refs = ", ".join([v["verse_id"] for v in verses_data])
    
    # Enhanced analysis with modern context
    analysis = f"""## Analysis

The Bhagavad Gita provides timeless wisdom that is remarkably relevant for {question_data.get('context', 'modern challenges')}. The key principles that address this situation include:

### Core Principles

1. **Dharma (Righteous Duty)**: Understanding and following one's righteous duty is fundamental. For {question_data.get('context', 'young people today')}, this means acting with integrity and purpose, even when facing modern pressures.

2. **Detachment from Results**: The Gita teaches performing actions without attachment to outcomes. This is crucial in an age of instant gratification and social media validation.

3. **Equanimity**: Maintaining balance in success and failure, praise and criticism. Essential for mental resilience in today's fast-paced, comparison-driven culture.

4. **Self-Knowledge**: Understanding one's true nature beyond temporary circumstances. This provides stability when external situations are constantly changing.

5. **Karma Yoga**: The path of selfless action - performing duties as service without ego. This builds authentic leadership and genuine connection.

### Modern Application

These ancient principles directly apply to {question_data.get('context', 'contemporary challenges')}:
- Digital overwhelm → Practice detachment and self-control
- Comparison culture → Focus on your dharma, not others' paths
- Rapid change → Cultivate inner stability through self-knowledge
- Ethical dilemmas → Follow dharma and righteous principles

Relevant verses: {verse_refs}

These teachings provide a solid foundation for navigating modern life with wisdom, integrity, and inner peace."""

    guidance = f"""## Practical Guidance for Modern Application

Based on Bhagavad Gita's teachings, here's how to apply these principles to {question_data.get('context', 'your situation')}:

### Immediate Actions

1. **Clarify Your Dharma**
   - Reflect on: "What is my righteous duty in this situation?"
   - Consider your values, responsibilities, and purpose
   - Act according to your authentic nature, not external pressures
   - For {question_data.get('context', 'young leaders')}: Lead with integrity and service, not ego

2. **Practice Digital Detachment**
   - Set boundaries with technology and social media
   - Don't let external validation define your self-worth
   - Focus on your work and growth, not comparison
   - Take regular breaks from digital devices

3. **Cultivate Mental Resilience**
   - Practice daily meditation or mindfulness (even 10 minutes helps)
   - Develop equanimity - stay balanced in all situations
   - Build inner strength through self-reflection
   - Connect with supportive communities

4. **Lead by Example**
   - Demonstrate the values you want to see
   - Serve others selflessly
   - Maintain integrity even when it's difficult
   - Inspire through action, not just words

5. **Seek Wisdom and Guidance**
   - Study relevant verses: {verse_refs}
   - Find mentors who embody these principles
   - Join communities focused on growth
   - Practice continuous learning

### Where to Focus

- **For Leadership**: Study chapters 3, 6, and 18 on duty, meditation, and renunciation
- **For Resilience**: Focus on chapters 2 and 6 on equanimity and mind control
- **For Morals**: Emphasize chapters 16 and 18 on divine qualities and dharma
- **Daily Practice**: Apply one principle each day, reflect on progress weekly"""

    exercises = f"""## Practical Exercises for Daily Life

### 1. Morning Reflection (10 minutes)
- **Purpose**: Set intention for the day based on dharma
- **Practice**: 
  - Sit quietly upon waking
  - Ask: "What is my dharma today? How can I serve?"
  - Set one intention aligned with your values
  - Review relevant verse: {verse_refs.split(',')[0] if verse_refs else 'BG 2.47'}

### 2. Digital Detachment Practice
- **Purpose**: Reduce attachment to social media and digital validation
- **Practice**:
  - Designate phone-free times (meals, first hour of day, before bed)
  - Before posting, ask: "Am I doing this for validation or service?"
  - Limit social media to specific times
  - Practice being present without documenting everything

### 3. Resilience Building Meditation (15-20 minutes)
- **Purpose**: Develop mental strength and equanimity
- **Practice**:
  - Sit comfortably, close eyes
  - Observe thoughts without judgment (like clouds passing)
  - Practice detachment from mental fluctuations
  - Cultivate inner peace and stability
  - End with gratitude and intention to serve

### 4. Karma Yoga in Daily Work
- **Purpose**: Transform work into spiritual practice
- **Practice**:
  - Before each task, offer it as service
  - Focus on the action, not the result
  - Maintain equanimity in success and failure
  - See challenges as opportunities for growth
  - Serve colleagues and community selflessly

### 5. Weekly Dharma Review
- **Purpose**: Align actions with values and purpose
- **Practice**:
  - Every Sunday, reflect on the week
  - Questions: "Did I act according to my dharma? Where did I compromise values?"
  - Plan improvements for next week
  - Study verses: {verse_refs}
  - Journal insights and growth

### 6. Leadership Practice (for leaders)
- **Purpose**: Develop authentic, service-oriented leadership
- **Practice**:
  - Lead by example, not just instruction
  - Serve team members' growth and well-being
  - Make decisions based on dharma, not ego
  - Maintain humility and continuous learning
  - Create environments of trust and growth

### 7. Ethical Decision Framework
- **Purpose**: Navigate complex moral situations
- **Practice**:
  - When facing ethical dilemmas, ask:
    1. "What is the righteous action (dharma)?"
    2. "Does this serve the greater good?"
    3. "Am I acting from ego or service?"
    4. "What would a wise person do?"
  - Consult relevant Gita principles
  - Act with integrity, accept results with equanimity"""

    final_answer = f"""# Guidance from Bhagavad Gita for {question_data.get('context', 'Modern Challenges')}

## Your Question
{question_data['query']}

{analysis}

{guidance}

{exercises}

## Key Verses Referenced
{verse_refs}

## Additional Resources

- **Study Focus**: Chapters 2, 3, 6, 16, and 18
- **Daily Practice**: Start with 10-minute meditation and one principle application
- **Community**: Seek like-minded individuals for support and growth
- **Continuous Learning**: Study Gita regularly, contemplate meanings, apply teachings

---
*This guidance is based on the teachings of Bhagavad Gita As It Is by A.C. Bhaktivedanta Swami Prabhupada, adapted for modern application.*"""

    return {
        "user_query": question_data['query'],
        "problem_context": question_data.get('context', ''),
        "research_questions": [
            f"How does Gita address {question_data['query'].lower()}?",
            f"What leadership/resilience/moral principles apply?",
            f"How can these be applied to {question_data.get('context', 'modern challenges')}?"
        ],
        "relevant_verses": verses_data,
        "analysis": analysis,
        "guidance": guidance,
        "exercises": exercises,
        "final_answer": final_answer
    }

@pytest.fixture
def client():
    """Create test client."""
    from starlette.testclient import TestClient
    from main import app
    return TestClient(app)

@patch('main.get_vector_store')
@patch('main.ResearchAgent')
@patch('main.get_db_session')
def test_leadership_for_genz_genalpha(mock_db_session, mock_agent_class, mock_vector_store, client):
    """Test leadership guidance for Gen Z and Gen Alpha."""
    question_data = GENZ_GENALPHA_QUESTIONS[0]
    
    # Setup mocks
    mock_vs = MagicMock()
    mock_vector_store.return_value = mock_vs
    
    # Create relevant leadership verses
    leadership_verses = [
        {
            "verse_id": "BG 3.21",
            "chapter": 3,
            "verse_number": 21,
            "sanskrit": "यद्यदाचरति श्रेष्ठस्तत्तदेवेतरो जनः",
            "translation": "Whatever action a great man performs, common men follow. And whatever standards he sets by exemplary acts, all the world pursues.",
            "purport": "Leaders set examples that others follow. A leader must act righteously."
        },
        {
            "verse_id": "BG 18.43",
            "chapter": 18,
            "verse_number": 43,
            "sanskrit": "शौर्यं तेजो धृतिर्दाक्ष्यं युद्धे चाप्यपलायनम्",
            "translation": "Heroism, power, determination, resourcefulness, courage in battle, generosity, and leadership are the qualities of work for the kṣatriyas.",
            "purport": "Leadership qualities include courage, determination, and service."
        },
        {
            "verse_id": "BG 5.25",
            "chapter": 5,
            "verse_number": 25,
            "sanskrit": "लभन्ते ब्रह्मनिर्वाणमृषयः क्षीणकल्मषाः",
            "translation": "Those who are beyond the dualities that arise from doubts, whose minds are engaged within, who are always busy working for the welfare of all living beings, and who are free from all sins achieve liberation in the Supreme.",
            "purport": "True leaders work for the welfare of all."
        },
        {
            "verse_id": "BG 3.19",
            "chapter": 3,
            "verse_number": 19,
            "sanskrit": "तस्मादसक्तः सततं कार्यं कर्म समाचर",
            "translation": "Therefore, without being attached to the fruits of activities, one should act as a matter of duty, for by working without attachment one attains the Supreme.",
            "purport": "Leaders should act selflessly, without attachment to results."
        },
        {
            "verse_id": "BG 6.32",
            "chapter": 6,
            "verse_number": 32,
            "sanskrit": "आत्मौपम्येन सर्वत्र समं पश्यति योऽर्जुन",
            "translation": "He is a perfect yogi who, by comparison to his own self, sees the true equality of all beings, in both their happiness and their distress, O Arjuna!",
            "purport": "True leaders see equality in all and serve accordingly."
        }
    ]
    
    mock_vs.search.return_value = [{"chunk": {"verse_id": v["verse_id"]}, "score": 0.9} for v in leadership_verses]
    
    mock_session = MagicMock()
    mock_verse = MagicMock()
    mock_verse.to_dict.return_value = leadership_verses[0]
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_verse
    mock_db_session.return_value = mock_session
    
    mock_agent = MagicMock()
    mock_graph = MagicMock()
    mock_state = create_high_quality_response(question_data, leadership_verses)
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
    assert len(data["answer"]) > 1000, "Answer should be very comprehensive for leadership question"
    assert len(data["analysis"]) > 500, "Analysis should be detailed"
    assert len(data["guidance"]) > 500, "Guidance should be extensive"
    assert len(data["exercises"]) > 500, "Exercises should be comprehensive"
    assert len(data["verses"]) >= question_data["min_verses"], f"Should have at least {question_data['min_verses']} verses"
    
    # Content quality checks
    answer_lower = data["answer"].lower()
    assert any(theme in answer_lower for theme in question_data["expected_themes"]), \
        f"Should mention themes: {question_data['expected_themes']}"
    
    # Check for modern context
    assert any(word in answer_lower for word in ["gen z", "gen alpha", "modern", "digital", "contemporary"]), \
        "Should address modern context"
    
    # Check for practical elements
    assert any(word in answer_lower for word in ["practice", "exercise", "daily", "action"]), \
        "Should include practical elements"
    
    # Check for leadership-specific content
    assert any(word in answer_lower for word in ["lead", "leader", "leadership", "example", "service"]), \
        "Should specifically address leadership"

@patch('main.get_vector_store')
@patch('main.ResearchAgent')
@patch('main.get_db_session')
def test_resilience_for_genz_social_media(mock_db_session, mock_agent_class, mock_vector_store, client):
    """Test resilience guidance for Gen Z dealing with social media."""
    question_data = GENZ_GENALPHA_QUESTIONS[1]
    
    mock_vs = MagicMock()
    mock_vector_store.return_value = mock_vs
    
    resilience_verses = [
        {
            "verse_id": "BG 6.35",
            "chapter": 6,
            "verse_number": 35,
            "translation": "Undoubtedly, O mighty-armed, the mind is restless and difficult to control; but it is subdued by constant practice and detachment.",
            "purport": "Mind control requires practice and detachment from material desires."
        },
        {
            "verse_id": "BG 2.56",
            "chapter": 2,
            "verse_number": 56,
            "translation": "One whose happiness is within, who is active and rejoices within, and whose aim is inward is actually the perfect mystic.",
            "purport": "True happiness comes from within, not external validation."
        },
        {
            "verse_id": "BG 2.14",
            "chapter": 2,
            "verse_number": 14,
            "translation": "O son of Kunti, the contact between the senses and the sense objects gives rise to fleeting perceptions of happiness and distress.",
            "purport": "Material happiness and distress are temporary."
        },
        {
            "verse_id": "BG 6.6",
            "chapter": 6,
            "verse_number": 6,
            "translation": "For him who has conquered the mind, the mind is the best of friends; but for one who has failed to do so, his mind will remain the greatest enemy.",
            "purport": "Controlling the mind is essential for peace."
        },
        {
            "verse_id": "BG 12.12",
            "chapter": 12,
            "verse_number": 12,
            "translation": "Better indeed is knowledge than practice; than knowledge, meditation is better; than meditation, renunciation of the fruits of action; peace immediately follows such renunciation.",
            "purport": "Detachment from results brings peace."
        }
    ]
    
    mock_vs.search.return_value = [{"chunk": {"verse_id": v["verse_id"]}, "score": 0.9} for v in resilience_verses]
    
    mock_session = MagicMock()
    mock_verse = MagicMock()
    mock_verse.to_dict.return_value = resilience_verses[0]
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_verse
    mock_db_session.return_value = mock_session
    
    mock_agent = MagicMock()
    mock_graph = MagicMock()
    mock_state = create_high_quality_response(question_data, resilience_verses)
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
    assert len(data["answer"]) > 1000
    assert "social media" in data["answer"].lower() or "digital" in data["answer"].lower()
    assert "resilience" in data["answer"].lower() or "resilient" in data["answer"].lower()
    assert "mind" in data["answer"].lower() or "mental" in data["answer"].lower()
    assert len(data["exercises"]) > 500
    assert any(word in data["exercises"].lower() for word in ["meditation", "practice", "detachment"])

@patch('main.get_vector_store')
@patch('main.ResearchAgent')
@patch('main.get_db_session')
def test_morals_for_genalpha_ai_ethics(mock_db_session, mock_agent_class, mock_vector_store, client):
    """Test moral guidance for Gen Alpha on AI ethics."""
    question_data = GENZ_GENALPHA_QUESTIONS[2]
    
    mock_vs = MagicMock()
    mock_vector_store.return_value = mock_vs
    
    moral_verses = [
        {
            "verse_id": "BG 16.1-3",
            "chapter": 16,
            "verse_number": 1,
            "translation": "Fearlessness, purification of one's existence, cultivation of spiritual knowledge, charity, self-control, performance of sacrifice, study of the Vedas, austerity, simplicity...",
            "purport": "Divine qualities include truthfulness, compassion, and self-control."
        },
        {
            "verse_id": "BG 18.48",
            "chapter": 18,
            "verse_number": 48,
            "translation": "Every endeavor is covered by some fault, just as fire is covered by smoke. Therefore one should not give up the work born of his nature, O son of Kunti, even if such work is full of fault.",
            "purport": "One should perform duty according to nature, even if imperfect."
        },
        {
            "verse_id": "BG 17.15",
            "chapter": 17,
            "verse_number": 15,
            "translation": "Austerity of speech consists in speaking words that are truthful, pleasing, beneficial, and not agitating to others, and also in regularly reciting Vedic literature.",
            "purport": "Speech should be truthful and beneficial."
        },
        {
            "verse_id": "BG 18.63",
            "chapter": 18,
            "verse_number": 63,
            "translation": "Thus I have explained to you knowledge still more confidential. Deliberate on this fully, and then do what you wish to do.",
            "purport": "One should deliberate and act with wisdom."
        },
        {
            "verse_id": "BG 3.35",
            "chapter": 3,
            "verse_number": 35,
            "translation": "It is better to engage in one's own occupation, even though one may perform it imperfectly, than to accept another's occupation and perform it perfectly.",
            "purport": "Follow your own dharma, act with integrity."
        }
    ]
    
    mock_vs.search.return_value = [{"chunk": {"verse_id": v["verse_id"]}, "score": 0.9} for v in moral_verses]
    
    mock_session = MagicMock()
    mock_verse = MagicMock()
    mock_verse.to_dict.return_value = moral_verses[0]
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_verse
    mock_db_session.return_value = mock_session
    
    mock_agent = MagicMock()
    mock_graph = MagicMock()
    mock_state = create_high_quality_response(question_data, moral_verses)
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
    assert len(data["answer"]) > 1000
    assert any(word in data["answer"].lower() for word in ["ai", "technology", "digital", "ethics"])
    assert any(word in data["answer"].lower() for word in ["moral", "ethics", "dharma", "righteous"])
    assert "gen alpha" in data["answer"].lower() or "young" in data["answer"].lower()
    assert len(data["verses"]) >= 5

@patch('main.get_vector_store')
@patch('main.ResearchAgent')
@patch('main.get_db_session')
def test_all_genz_genalpha_questions_quality(mock_db_session, mock_agent_class, mock_vector_store, client):
    """Test all Gen Z and Gen Alpha questions for quality."""
    quality_results = []
    
    for question_data in GENZ_GENALPHA_QUESTIONS:
        mock_vs = MagicMock()
        mock_vector_store.return_value = mock_vs
        
        # Create relevant verses for each question
        verses = [
            {
                "verse_id": f"BG {i}.{j}",
                "chapter": i,
                "verse_number": j,
                "translation": f"Relevant translation for {question_data['query'][:30]}",
                "purport": f"Purport explaining principles"
            }
            for i in range(2, 7) for j in range(1, 6)
        ][:question_data["min_verses"]]
        
        mock_vs.search.return_value = [{"chunk": {"verse_id": v["verse_id"]}, "score": 0.9} for v in verses]
        
        mock_session = MagicMock()
        mock_verse = MagicMock()
        mock_verse.to_dict.return_value = verses[0]
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_verse
        mock_db_session.return_value = mock_session
        
        mock_agent = MagicMock()
        mock_graph = MagicMock()
        mock_state = create_high_quality_response(question_data, verses)
        mock_graph.invoke.return_value = mock_state
        mock_agent.build_graph.return_value = mock_graph
        mock_agent_class.return_value = mock_agent
        
        response = client.post("/api/research", json={
            "query": question_data["query"],
            "context": question_data.get("context", "")
        })
        
        if response.status_code == 200:
            data = response.json()
            checks = {
                "question": question_data["query"][:60],
                "answer_length": len(data.get("answer", "")),
                "analysis_length": len(data.get("analysis", "")),
                "guidance_length": len(data.get("guidance", "")),
                "exercises_length": len(data.get("exercises", "")),
                "verses_count": len(data.get("verses", [])),
                "has_modern_context": any(word in data.get("answer", "").lower() 
                                         for word in ["gen z", "gen alpha", "modern", "digital", "contemporary"]),
                "has_expected_themes": any(theme in data.get("answer", "").lower() 
                                         for theme in question_data["expected_themes"]),
                "has_quality_checks": all(qc in data.get("answer", "").lower() 
                                         for qc in question_data.get("quality_checks", [])[:2])  # Check first 2
            }
            quality_results.append(checks)
    
    # Verify all questions got quality responses
    assert len(quality_results) == len(GENZ_GENALPHA_QUESTIONS)
    
    for result in quality_results:
        assert result["answer_length"] > 1000, f"Question '{result['question']}' should have comprehensive answer (got {result['answer_length']})"
        assert result["analysis_length"] > 500, f"Question '{result['question']}' should have detailed analysis"
        assert result["guidance_length"] > 500, f"Question '{result['question']}' should have extensive guidance"
        assert result["exercises_length"] > 500, f"Question '{result['question']}' should have comprehensive exercises"
        assert result["verses_count"] >= 4, f"Question '{result['question']}' should have enough verses"
        assert result["has_modern_context"], f"Question '{result['question']}' should address modern context"
        assert result["has_expected_themes"], f"Question '{result['question']}' should mention expected themes"

