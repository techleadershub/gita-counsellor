from pydantic import BaseModel, Field
from typing import Optional, Dict
from sqlalchemy import create_engine, Column, String, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DB_PATH
import os

# SQLAlchemy Models
Base = declarative_base()

class Verse(Base):
    __tablename__ = "verses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    verse_id = Column(String, unique=True, index=True)  # e.g., "BG 2.12"
    chapter = Column(Integer, index=True)
    verse_number = Column(Integer, index=True)
    sanskrit = Column(Text)
    synonyms = Column(Text)
    translation = Column(Text)
    purport = Column(Text)
    
    def to_dict(self):
        # Extract transliteration and word meanings from synonyms field
        transliteration = None
        word_meanings = None
        
        if self.synonyms:
            # Format: transliteration + "\n" + word_meanings
            # Parse line by line to separate transliteration (multiple lines) from word meanings
            lines = self.synonyms.split('\n')
            transliteration_lines = []
            word_meanings_lines = []
            found_word_meanings_start = False
            
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    if not found_word_meanings_start:
                        transliteration_lines.append(line_stripped)
                    else:
                        word_meanings_lines.append(line_stripped)
                    continue
                
                # Check if this line starts word meanings (has "—" or ":" pattern)
                if '—' in line_stripped or (':' in line_stripped and len(line_stripped.split(':')) > 1):
                    found_word_meanings_start = True
                    word_meanings_lines.append(line_stripped)
                elif found_word_meanings_start:
                    word_meanings_lines.append(line_stripped)
                else:
                    transliteration_lines.append(line_stripped)
            
            # Join transliteration lines (preserve line breaks)
            if transliteration_lines:
                transliteration = '\n'.join(transliteration_lines).strip()
                if not transliteration:
                    transliteration = None
            
            # Filter out chapter-ending notes (edge case for last verses)
            # These are notes like "Thus end the Bhaktivedanta Purports to the [X] Chapter..."
            if transliteration:
                transliteration_lower = transliteration.lower()
                chapter_ending_phrases = [
                    'thus end',
                    'thus ends',
                    'end the',
                    'ends the',
                    'bhaktivedanta purports',
                    'concluding statement',
                    'end of chapter'
                ]
                # Check if transliteration is actually a chapter-ending note
                if any(phrase in transliteration_lower for phrase in chapter_ending_phrases):
                    # This is a chapter-ending note, not transliteration
                    transliteration = None
                    # If we have word meanings, they might actually be the transliteration
                    # But typically chapter-ending notes don't have real transliteration
                    # So we'll just set transliteration to None
            
            # Join word meanings lines
            if word_meanings_lines:
                word_meanings = '\n'.join(word_meanings_lines).strip()
                if not word_meanings:
                    word_meanings = None
        
        return {
            "verse_id": self.verse_id,
            "chapter": self.chapter,
            "verse_number": self.verse_number,
            "transliteration": transliteration,
            "word_meanings": word_meanings,
            "translation": self.translation,
            "purport": self.purport
        }

# Database setup
def get_db_engine():
    os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else ".", exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    Base.metadata.create_all(engine)
    return engine

def get_db_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()

# Pydantic Models for API
class VerseChunk(BaseModel):
    verse_id: str = Field(..., description="Unique ID, e.g., 'BG 2.12'")
    chapter: int = Field(..., description="Chapter number")
    verse_number: int = Field(..., description="Verse number")
    
    # Content
    sanskrit: Optional[str] = None
    synonyms: Optional[str] = None
    translation: str
    purport: Optional[str] = None
    
    # Metadata for search relevance
    metadata: Dict = Field(default_factory=dict)

    def to_text_for_embedding(self) -> str:
        """Creates the text representation for embedding."""
        parts = []
        parts.append(f"Verse: {self.verse_id}")
        if self.sanskrit:
            parts.append(f"Sanskrit: {self.sanskrit}")
        if self.synonyms:
            parts.append(f"Synonyms: {self.synonyms}")
        if self.translation:
            parts.append(f"Translation: {self.translation}")
        if self.purport:
            parts.append(f"Purport: {self.purport}")
        return "\n\n".join(parts)

