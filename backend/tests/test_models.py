import pytest
from models import VerseChunk, Verse, get_db_engine, get_db_session, Base

def test_verse_chunk_creation(sample_verse_chunk):
    """Test VerseChunk creation."""
    assert sample_verse_chunk.verse_id == "BG 2.12"
    assert sample_verse_chunk.chapter == 2
    assert sample_verse_chunk.verse_number == 12
    assert sample_verse_chunk.translation is not None

def test_verse_chunk_to_text_for_embedding(sample_verse_chunk):
    """Test verse chunk text generation for embedding."""
    text = sample_verse_chunk.to_text_for_embedding()
    assert "BG 2.12" in text
    assert "Sanskrit:" in text
    assert "Translation:" in text
    assert "Purport:" in text

def test_verse_chunk_minimal():
    """Test VerseChunk with minimal required fields."""
    chunk = VerseChunk(
        verse_id="BG 1.1",
        chapter=1,
        verse_number=1,
        translation="Test translation"
    )
    assert chunk.verse_id == "BG 1.1"
    assert chunk.sanskrit is None
    assert chunk.purport is None

def test_verse_db_model(mock_db_session, sample_verse_data, monkeypatch):
    """Test Verse database model."""
    # Clear any existing verse first
    mock_db_session.query(Verse).filter_by(verse_id="BG 2.12").delete()
    mock_db_session.commit()
    
    verse = Verse(**sample_verse_data)
    mock_db_session.add(verse)
    mock_db_session.commit()
    
    retrieved = mock_db_session.query(Verse).filter_by(verse_id="BG 2.12").first()
    assert retrieved is not None
    assert retrieved.chapter == 2
    assert retrieved.verse_number == 12
    assert retrieved.translation == sample_verse_data["translation"]

def test_verse_to_dict(sample_verse_data, mock_db_session):
    """Test Verse to_dict method."""
    # Clear any existing verse first
    mock_db_session.query(Verse).filter_by(verse_id="BG 2.12").delete()
    mock_db_session.commit()
    
    verse = Verse(**sample_verse_data)
    mock_db_session.add(verse)
    mock_db_session.commit()
    
    verse_dict = verse.to_dict()
    assert isinstance(verse_dict, dict)
    assert verse_dict["verse_id"] == "BG 2.12"
    assert verse_dict["chapter"] == 2
    assert "translation" in verse_dict

def test_verse_query_by_chapter(mock_db_session, sample_verse_data):
    """Test querying verses by chapter."""
    # Clear existing verses
    mock_db_session.query(Verse).filter_by(chapter=2).delete()
    mock_db_session.commit()
    
    verse1 = Verse(**sample_verse_data)
    verse2_data = sample_verse_data.copy()
    verse2_data["verse_id"] = "BG 2.13"
    verse2_data["verse_number"] = 13
    verse2 = Verse(**verse2_data)
    
    mock_db_session.add_all([verse1, verse2])
    mock_db_session.commit()
    
    verses = mock_db_session.query(Verse).filter_by(chapter=2).all()
    assert len(verses) == 2
    assert all(v.chapter == 2 for v in verses)

