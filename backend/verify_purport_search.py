"""
Script to verify that purports are being used in vector search and included in context.

This script:
1. Finds a verse with a purport
2. Extracts unique keywords/phrases from the purport that are NOT in the translation
3. Searches using those unique purport-only terms
4. Verifies the verse is found
5. Shows what context is being sent to the LLM
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import get_db_session, Verse
from vector_store import get_vector_store
import re

def get_unique_purport_terms(verse):
    """Extract unique terms from purport that are NOT in translation."""
    translation = (verse.translation or "").lower()
    purport = (verse.purport or "").lower()
    
    if not purport:
        return []
    
    # Extract meaningful words from purport (3+ characters, not common words)
    common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
                   'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
                   'this', 'that', 'these', 'those', 'a', 'an', 'as', 'it', 'its', 'he', 'she', 'they'}
    
    # Get words from purport
    purport_words = set(re.findall(r'\b[a-z]{3,}\b', purport))
    translation_words = set(re.findall(r'\b[a-z]{3,}\b', translation))
    
    # Find words unique to purport
    unique_words = purport_words - translation_words - common_words
    
    # Also extract unique phrases (2-3 word combinations)
    purport_phrases = []
    words_list = re.findall(r'\b[a-z]{3,}\b', purport)
    for i in range(len(words_list) - 1):
        phrase = f"{words_list[i]} {words_list[i+1]}"
        if phrase not in translation.lower():
            purport_phrases.append(phrase)
    
    return list(unique_words)[:10], purport_phrases[:5]  # Return top 10 words and 5 phrases

def verify_purport_in_embedding(verse_id):
    """Verify that a specific verse's embedding includes purport content."""
    db_session = get_db_session()
    verse = db_session.query(Verse).filter_by(verse_id=verse_id).first()
    db_session.close()
    
    if not verse:
        print(f"❌ Verse {verse_id} not found in database")
        return False
    
    if not verse.purport:
        print(f"❌ Verse {verse_id} has no purport")
        return False
    
    print(f"\n📖 Verse: {verse_id}")
    print(f"   Translation: {verse.translation[:100]}...")
    print(f"   Purport length: {len(verse.purport)} characters")
    
    # Get unique purport terms
    unique_words, unique_phrases = get_unique_purport_terms(verse)
    
    if not unique_words:
        print("⚠️  No unique words found in purport (purport might be too similar to translation)")
        return False
    
    print(f"\n🔍 Unique purport terms (not in translation):")
    print(f"   Words: {', '.join(unique_words[:10])}")
    print(f"   Phrases: {', '.join(unique_phrases[:5])}")
    
    # Create a search query using unique purport terms
    search_query = f"{' '.join(unique_words[:5])} {unique_phrases[0] if unique_phrases else ''}"
    search_query = search_query.strip()
    
    print(f"\n🔎 Testing search with purport-only terms:")
    print(f"   Query: '{search_query}'")
    
    # Search vector store
    try:
        vs = get_vector_store()
        results = vs.search(search_query, limit=5)
        
        # Check if our verse is in results
        found = False
        for result in results:
            result_verse_id = result.get("verse_id", "") or result.get("chunk", {}).get("verse_id", "")
            if result_verse_id == verse_id:
                found = True
                score = result.get("score", 0)
                print(f"\n✅ SUCCESS! Verse {verse_id} found in search results!")
                print(f"   Relevance score: {score:.4f}")
                print(f"   Rank: {results.index(result) + 1}")
                break
        
        if not found:
            print(f"\n❌ Verse {verse_id} NOT found in search results")
            print(f"   Top results:")
            for i, result in enumerate(results[:3], 1):
                result_verse_id = result.get("verse_id", "") or result.get("chunk", {}).get("verse_id", "")
                score = result.get("score", 0)
                print(f"   {i}. {result_verse_id} (score: {score:.4f})")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during search: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_purport_in_context(verse_id):
    """Verify that purport is included in the context sent to LLM."""
    db_session = get_db_session()
    verse = db_session.query(Verse).filter_by(verse_id=verse_id).first()
    db_session.close()
    
    if not verse or not verse.purport:
        print(f"❌ Verse {verse_id} not found or has no purport")
        return False
    
    # Simulate what research_agent does
    verse_dict = verse.to_dict()
    
    # Format as research_agent does
    transliteration = verse_dict.get('transliteration', 'N/A')
    word_meanings = verse_dict.get('word_meanings', 'N/A')
    verse_text = f"""
Verse {verse_dict['verse_id']} (Chapter {verse_dict['chapter']}, Verse {verse_dict['verse_number']}):
Transliteration: {transliteration}
Word Meanings: {word_meanings}
Translation: {verse_dict.get('translation', 'N/A')}
Purport: {verse_dict.get('purport', 'N/A')}
"""
    
    print(f"\n📋 Context that would be sent to LLM:")
    print("=" * 80)
    print(verse_text)
    print("=" * 80)
    
    # Verify purport is present
    if 'Purport:' in verse_text and verse_dict.get('purport'):
        purport_in_context = verse_dict.get('purport', '')
        print(f"\n✅ Purport is included in context!")
        print(f"   Purport length: {len(purport_in_context)} characters")
        print(f"   Purport preview: {purport_in_context[:200]}...")
        return True
    else:
        print(f"\n❌ Purport is NOT included in context!")
        return False

def find_verses_with_purports(limit=5):
    """Find verses that have purports."""
    db_session = get_db_session()
    verses = db_session.query(Verse).filter(Verse.purport.isnot(None), Verse.purport != '').limit(limit).all()
    db_session.close()
    
    print(f"\n📚 Found {len(verses)} verses with purports:")
    for verse in verses:
        print(f"   - {verse.verse_id}: {len(verse.purport)} chars in purport")
    
    return verses

def main():
    print("=" * 80)
    print("VERIFYING PURPORT USAGE IN SEARCH AND CONTEXT")
    print("=" * 80)
    
    # Step 1: Find verses with purports
    print("\n[STEP 1] Finding verses with purports...")
    verses = find_verses_with_purports(limit=10)
    
    if not verses:
        print("❌ No verses with purports found in database!")
        return
    
    # Step 2: Test with first verse that has a substantial purport
    test_verse = None
    for verse in verses:
        if verse.purport and len(verse.purport) > 200:  # Substantial purport
            test_verse = verse
            break
    
    if not test_verse:
        test_verse = verses[0]
    
    verse_id = test_verse.verse_id
    
    # Step 3: Verify purport is in embedding/search
    print(f"\n[STEP 2] Verifying purport content is searchable...")
    search_success = verify_purport_in_embedding(verse_id)
    
    # Step 4: Verify purport is in context
    print(f"\n[STEP 3] Verifying purport is included in LLM context...")
    context_success = verify_purport_in_context(verse_id)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Purport in vector embeddings/search: {'YES' if search_success else 'NO'}")
    print(f"✅ Purport in LLM context: {'YES' if context_success else 'NO'}")
    
    if search_success and context_success:
        print("\n🎉 SUCCESS! Purports are being used in both search and context!")
    elif context_success:
        print("\n⚠️  WARNING: Purports are in context but may not be searchable")
    else:
        print("\n❌ ERROR: Purports are not being properly included")

if __name__ == "__main__":
    main()

