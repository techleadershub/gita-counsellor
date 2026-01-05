import os
import re
from typing import List, Optional
from bs4 import BeautifulSoup, NavigableString, Tag
import ebooklib
from ebooklib import epub
try:
    from .models import VerseChunk, Verse, get_db_session
    from .vector_store import VectorStore
except ImportError:
    from models import VerseChunk, Verse, get_db_session
    from vector_store import VectorStore
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ingestion.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        # Regex for BG chapter.verse (e.g., BG 2.12 or 2.12)
        self.verse_pattern = re.compile(r'\b(BG|Gita)?\s*(\d+)\.(\d+)\b', re.IGNORECASE)

    def process_epub(self, epub_path: str) -> List[VerseChunk]:
        """Process Bhagavad Gita EPUB file and extract verses."""
        book = epub.read_epub(epub_path)
        chunks = []
        book_title = "Bhagavad Gita As It Is"
        
        db_session = get_db_session()
        # Initialize chapter outside item loop to persist across document items
        current_chapter = None
        current_verse_num = None
        
        def save_chunk(chunk):
            """Save a verse chunk to database and add to chunks list."""
            if not chunk or not chunk.get("verse_id"):
                return
            
            verse_id = chunk["verse_id"]
            chapter = chunk.get("chapter", 0)
            verse_num = chunk.get("verse_number", 0)
            
            # Clean up content
            sanskrit = chunk.get("sanskrit", "").strip()
            transliteration = chunk.get("transliteration", "").strip()
            synonyms = chunk.get("synonyms", "").strip()
            translation = chunk.get("translation", "").strip()
            purport = chunk.get("purport", "").strip()
            
            # Validation: Must have at least translation
            if not translation:
                return
            
            # Create VerseChunk for vector store
            verse_chunk = VerseChunk(
                verse_id=verse_id,
                chapter=chapter,
                verse_number=verse_num,
                sanskrit=sanskrit if sanskrit else None,
                synonyms=synonyms if synonyms else None,
                translation=translation,
                purport=purport if purport else None
            )
            chunks.append(verse_chunk)
            
            # Save to SQLite database
            try:
                # Check if verse already exists
                existing = db_session.query(Verse).filter_by(verse_id=verse_id).first()
                if existing:
                    # Update existing verse
                    existing.sanskrit = sanskrit
                    existing.synonyms = synonyms
                    existing.translation = translation
                    existing.purport = purport
                else:
                    # Create new verse
                    verse_db = Verse(
                        verse_id=verse_id,
                        chapter=chapter,
                        verse_number=verse_num,
                        sanskrit=sanskrit,
                        synonyms=synonyms,
                        translation=translation,
                        purport=purport
                    )
                    db_session.add(verse_db)
                db_session.commit()
            except Exception as e:
                logger.error(f"Error saving verse {verse_id} to database: {e}")
                db_session.rollback()
        
        # Process each document item
        # Note: current_chapter persists across items to handle chapter boundaries
        current_chunk = None
        
        for item in book.get_items():
            if item.get_type() != ebooklib.ITEM_DOCUMENT:
                continue
            
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            
            # Get all divs in order
            divs = soup.find_all('div')
            
            # State tracking (reset per item, but chapter persists)
            state = "seeking"  # seeking, verse, transliteration, synonyms, translation, purport
            
            for div in divs:
                classes = div.get('class', [])
                text = div.get_text().strip()
                
                if not text:
                    continue
                
                # 1. Detect Chapter
                if 'verse-chap' in classes or ('calibre38' in classes and 'CHAPTER' in text.upper()):
                    # Extract chapter number
                    chapter_match = re.search(r'CHAPTER\s+(\w+)', text, re.IGNORECASE)
                    if chapter_match:
                        chapter_word = chapter_match.group(1).upper()
                        # Convert word to number (ONE -> 1, TWO -> 2, etc.)
                        chapter_map = {
                            'ONE': 1, 'TWO': 2, 'THREE': 3, 'FOUR': 4, 'FIVE': 5,
                            'SIX': 6, 'SEVEN': 7, 'EIGHT': 8, 'NINE': 9, 'TEN': 10,
                            'ELEVEN': 11, 'TWELVE': 12, 'THIRTEEN': 13, 'FOURTEEN': 14,
                            'FIFTEEN': 15, 'SIXTEEN': 16, 'SEVENTEEN': 17, 'EIGHTEEN': 18
                        }
                        current_chapter = chapter_map.get(chapter_word, None)
                        logger.debug(f"Found chapter: {current_chapter}")
                    continue
                
                # 2. Detect Verse Header (TEXT X)
                if 'verse-text' in classes:
                    # Save previous chunk if exists
                    if current_chunk:
                        save_chunk(current_chunk)
                    
                    # Extract verse number from "TEXT X"
                    verse_match = re.search(r'TEXT\s+(\d+)', text, re.IGNORECASE)
                    if verse_match and current_chapter:
                        current_verse_num = int(verse_match.group(1))
                        verse_id = f"BG {current_chapter}.{current_verse_num}"
                        
                        current_chunk = {
                            "verse_id": verse_id,
                            "chapter": current_chapter,
                            "verse_number": current_verse_num,
                            "sanskrit": "",
                            "transliteration": "",
                            "synonyms": "",
                            "translation": "",
                            "purport": ""
                        }
                        state = "verse"
                        logger.debug(f"Found verse: {verse_id}")
                    continue
                
                # 3. Process content based on state
                if current_chunk:
                    # Sanskrit (Devanagari script)
                    if 'verse' in classes and 'verse-text' not in classes and 'verse-chap' not in classes:
                        # Check if it contains Devanagari characters
                        if re.search(r'[अ-ह]', text):
                            if current_chunk["sanskrit"]:
                                current_chunk["sanskrit"] += "\n" + text
                            else:
                                current_chunk["sanskrit"] = text
                            state = "verse"
                            continue
                    
                    # Transliteration (romanized Sanskrit)
                    if 'verse-trs4' in classes or 'verse-trs5' in classes:
                        # Check if this is a chapter-ending note (edge case for last verses)
                        text_lower = text.lower()
                        chapter_ending_phrases = [
                            'thus end', 'thus ends', 'end the', 'ends the',
                            'bhaktivedanta purports', 'concluding statement', 'end of chapter'
                        ]
                        if any(phrase in text_lower for phrase in chapter_ending_phrases):
                            # Skip chapter-ending notes - don't save as transliteration
                            logger.debug(f"Skipping chapter-ending note for verse {current_chunk.get('verse_id', 'unknown')}")
                            continue
                        
                        if current_chunk["transliteration"]:
                            # Preserve line breaks - add newline if not empty, then add text
                            current_chunk["transliteration"] += "\n" + text
                        else:
                            current_chunk["transliteration"] = text
                        state = "transliteration"
                        continue
                    
                    # Synonyms/Word Meanings
                    if 'word-mean' in classes:
                        # Check if this is a chapter-ending note (edge case for last verses)
                        text_lower = text.lower()
                        chapter_ending_phrases = [
                            'thus end', 'thus ends', 'end the', 'ends the',
                            'bhaktivedanta purports', 'concluding statement', 'end of chapter'
                        ]
                        if any(phrase in text_lower for phrase in chapter_ending_phrases):
                            # Skip chapter-ending notes - don't save as word meanings
                            logger.debug(f"Skipping chapter-ending note for verse {current_chunk.get('verse_id', 'unknown')}")
                            continue
                        
                        # Combine transliteration with word meanings
                        if current_chunk["transliteration"]:
                            current_chunk["synonyms"] = current_chunk["transliteration"] + "\n" + text
                            current_chunk["transliteration"] = ""  # Clear it since we've combined
                        else:
                            current_chunk["synonyms"] = text
                        state = "synonyms"
                        continue
                    
                    # Translation header
                    if 'verse-hed1' in classes and 'TRANSLATION' in text.upper():
                        state = "translation"
                        continue
                    
                    # Translation content
                    if state == "translation" and 'data-trs' in classes:
                        if current_chunk["translation"]:
                            current_chunk["translation"] += " " + text
                        else:
                            current_chunk["translation"] = text
                        continue
                    
                    # Purport header
                    if 'verse-hed1' in classes and 'PURPORT' in text.upper():
                        state = "purport"
                        continue
                    
                    # Purport content
                    if state == "purport" and 'purport' in classes:
                        # Check if this is a chapter-ending note (edge case for last verses)
                        text_lower = text.lower()
                        chapter_ending_phrases = [
                            'thus end', 'thus ends', 'end the', 'ends the',
                            'bhaktivedanta purports', 'concluding statement', 'end of chapter'
                        ]
                        if any(phrase in text_lower for phrase in chapter_ending_phrases):
                            # Skip chapter-ending notes - don't save as purport
                            logger.debug(f"Skipping chapter-ending note for verse {current_chunk.get('verse_id', 'unknown')}")
                            continue
                        
                        if current_chunk["purport"]:
                            current_chunk["purport"] += "\n\n" + text
                        else:
                            current_chunk["purport"] = text
                        continue
                    
                    # Generic check for chapter-ending notes in any other div
                    # (some chapter-ending notes might appear in generic divs like calibre5)
                    if current_chunk:  # Only check if we're processing a verse
                        text_lower = text.lower()
                        chapter_ending_phrases = [
                            'thus end', 'thus ends', 'end the', 'ends the',
                            'bhaktivedanta purports', 'concluding statement', 'end of chapter'
                        ]
                        if any(phrase in text_lower for phrase in chapter_ending_phrases):
                            # Skip chapter-ending notes - don't process them
                            logger.debug(f"Skipping chapter-ending note (generic div) for verse {current_chunk.get('verse_id', 'unknown')}")
                            continue
            
            # Save last chunk if exists
            if current_chunk:
                # Final cleanup: remove any chapter-ending notes that might have been captured
                chapter_ending_phrases = [
                    'thus end', 'thus ends', 'end the', 'ends the',
                    'bhaktivedanta purports', 'concluding statement', 'end of chapter'
                ]
                
                # Check and clean transliteration
                if current_chunk.get("transliteration"):
                    transliteration_lower = current_chunk["transliteration"].lower()
                    if any(phrase in transliteration_lower for phrase in chapter_ending_phrases):
                        logger.debug(f"Removing chapter-ending note from transliteration for verse {current_chunk.get('verse_id', 'unknown')}")
                        current_chunk["transliteration"] = ""
                
                # Check and clean synonyms
                if current_chunk.get("synonyms"):
                    synonyms_lower = current_chunk["synonyms"].lower()
                    if any(phrase in synonyms_lower for phrase in chapter_ending_phrases):
                        logger.debug(f"Removing chapter-ending note from synonyms for verse {current_chunk.get('verse_id', 'unknown')}")
                        # If synonyms only contains chapter-ending note, clear it
                        # Otherwise, try to extract the part before the chapter-ending note
                        if synonyms_lower.startswith('thus end') or 'thus end' in synonyms_lower[:100]:
                            current_chunk["synonyms"] = ""
                        else:
                            # Try to find where chapter-ending note starts and remove it
                            for phrase in chapter_ending_phrases:
                                if phrase in synonyms_lower:
                                    idx = synonyms_lower.find(phrase)
                                    current_chunk["synonyms"] = current_chunk["synonyms"][:idx].strip()
                                    break
                
                # Combine any remaining transliteration with synonyms before saving
                if current_chunk.get("transliteration") and not current_chunk.get("synonyms"):
                    current_chunk["synonyms"] = current_chunk["transliteration"]
                elif current_chunk.get("transliteration") and current_chunk.get("synonyms"):
                    current_chunk["synonyms"] = current_chunk["transliteration"] + "\n" + current_chunk["synonyms"]
                save_chunk(current_chunk)
        
        db_session.close()
        logger.info(f"Processed {len(chunks)} verses from {epub_path}")
        return chunks

    def ingest_epub(self, epub_path: str = None):
        """Main ingestion function."""
        if epub_path is None:
            # Try default locations
            default_paths = [
                "./epubs/BhagavadGitaAsItIs.epub",
                "../epubs/BhagavadGitaAsItIs.epub",
                "/app/epubs/BhagavadGitaAsItIs.epub"
            ]
            for path in default_paths:
                if os.path.exists(path):
                    epub_path = path
                    break
            if epub_path is None:
                raise FileNotFoundError("EPUB file not found. Please specify path or place in ./epubs/")
        
        if not os.path.exists(epub_path):
            raise FileNotFoundError(f"EPUB file not found: {epub_path}")
        
        logger.info(f"Starting ingestion of {epub_path}")
        chunks = self.process_epub(epub_path)
        
        if chunks:
            logger.info(f"Ingesting {len(chunks)} chunks to vector store...")
            self.vector_store.add_chunks(chunks)
            logger.info("Ingestion complete!")
        else:
            logger.warning("No chunks extracted from EPUB")
        
        return len(chunks)
