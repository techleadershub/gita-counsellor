"""Ingest all verses from SQLite into Qdrant vector store"""
from vector_store import VectorStore
from models import get_db_session, Verse, VerseChunk
import sys

def ingest_all_verses():
    print("="*80)
    print("INGESTING ALL VERSES FROM SQLITE TO QDRANT")
    print("="*80)
    
    # Check current state
    db_session = get_db_session()
    try:
        total_verses = db_session.query(Verse).count()
        print(f"\nTotal verses in SQLite: {total_verses}")
    finally:
        db_session.close()
    
    vs = VectorStore()
    collection_info = vs.client.get_collection(vs.collection_name)
    current_points = collection_info.points_count
    print(f"Current points in Qdrant: {current_points}")
    
    if current_points > 0:
        print(f"\n⚠️  Qdrant already has {current_points} points. Continuing to add remaining verses...")
        # Optionally reset: vs.reset_db() and current_points = 0
    
    print(f"\nStarting ingestion...")
    
    # Get all verses from SQLite
    db_session = get_db_session()
    try:
        all_verses = db_session.query(Verse).order_by(Verse.chapter, Verse.verse_number).all()
        print(f"Retrieved {len(all_verses)} verses from SQLite")
        
        # Convert to VerseChunk and batch process
        batch_size = 50
        total_processed = 0
        total_added = 0
        
        for i in range(0, len(all_verses), batch_size):
            batch = all_verses[i:i+batch_size]
            chunks = []
            
            for v in batch:
                chunk = VerseChunk(
                    verse_id=v.verse_id,
                    chapter=v.chapter,
                    verse_number=v.verse_number,
                    sanskrit=v.sanskrit,
                    synonyms=v.synonyms,
                    translation=v.translation,
                    purport=v.purport
                )
                chunks.append(chunk)
            
            # Add batch to vector store
            try:
                vs.add_chunks(chunks)
                total_added += len(chunks)
                total_processed += len(chunks)
                
                if total_processed % 100 == 0 or total_processed == len(all_verses):
                    print(f"  Processed {total_processed}/{len(all_verses)} verses...")
                    
            except Exception as e:
                print(f"  ❌ Error adding batch {i//batch_size + 1}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n✅ Ingestion complete!")
        print(f"   Processed: {total_processed} verses")
        print(f"   Added: {total_added} verses")
        
        # Verify
        collection_info = vs.client.get_collection(vs.collection_name)
        final_points = collection_info.points_count
        print(f"   Final Qdrant points: {final_points}")
        
        if final_points == total_verses:
            print(f"   ✅ Perfect match! All verses indexed.")
        elif final_points > 0:
            print(f"   ⚠️  Point count ({final_points}) doesn't match verse count ({total_verses})")
        else:
            print(f"   ❌ ERROR: No points were added!")
        
        # Test search
        print(f"\nTesting search...")
        results = vs.search("What does the Bhagavad Gita say about duty?", limit=3)
        print(f"   Search returned {len(results)} results")
        for r in results[:3]:
            verse_id = r.get('verse_id', 'N/A')
            score = r.get('score', 0)
            print(f"     - {verse_id}: score {score:.4f}")
            
    finally:
        db_session.close()
    
    print("\n" + "="*80)
    print("INGESTION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    try:
        ingest_all_verses()
    except KeyboardInterrupt:
        print("\n\nIngestion interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

