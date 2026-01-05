from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import logging
import json
import asyncio
from vector_store import VectorStore
from research_agent import ResearchAgent
from ingestion import IngestionService
from models import get_db_session, Verse

app = FastAPI(title="Bhagavad Gita Research Agent API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
vector_store = None
ingestion_status = {"status": "idle", "message": "", "progress": 0}

# Initialize vector store
def get_vector_store():
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
    return vector_store

# Request Models
class ResearchRequest(BaseModel):
    query: str
    context: Optional[str] = None

class IngestionRequest(BaseModel):
    epub_path: Optional[str] = None

class VerseQuery(BaseModel):
    chapter: Optional[int] = None
    verse_number: Optional[int] = None
    verse_id: Optional[str] = None

# Logging callback for agent
def log_callback(message: str):
    logging.info(f"Agent: {message}")

@app.on_event("startup")
async def startup_event():
    os.makedirs("data", exist_ok=True)
    get_vector_store()

@app.get("/")
async def root():
    return {"message": "Bhagavad Gita Research Agent API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Progress queue for SSE - using thread-safe queue
import queue as thread_queue

async def research_with_progress(request: ResearchRequest):
    """Research with progress streaming via SSE."""
    progress_queue = thread_queue.Queue()
    
    def progress_callback(progress_data):
        """Callback to emit progress updates (called from sync context)."""
        try:
            # Queue.put() is blocking but unbounded queue won't block
            # Add timeout to prevent indefinite blocking (defensive)
            progress_queue.put(progress_data, block=True, timeout=5.0)
        except thread_queue.Full:
            # Queue is full (shouldn't happen with unbounded queue, but be safe)
            logging.warning("Progress queue full, dropping progress update")
        except Exception as e:
            # Don't let progress callback errors crash the research
            logging.error(f"Error putting progress data in queue: {e}")
    
    async def run_research():
        try:
            vs = get_vector_store()
            agent = ResearchAgent(vs, log_callback=log_callback, progress_callback=progress_callback)
            graph = agent.build_graph()
            
            initial_state = {
                "user_query": request.query,
                "problem_context": request.context or "",
                "research_questions": [],
                "relevant_verses": [],
                "analysis": "",
                "guidance": "",
                "exercises": "",
                "final_answer": ""
            }
            
            # Run research in background thread
            result = await asyncio.to_thread(graph.invoke, initial_state)
            
            # Send final result
            progress_queue.put({
                "step": "completed",
                "message": "Research complete!",
                "details": {
                    "answer": result["final_answer"],
                    "analysis": result["analysis"],
                    "guidance": result["guidance"],
                    "exercises": result["exercises"],
                    "verses": result["relevant_verses"][:10],
                    "query": request.query
                }
            })
        except Exception as e:
            logging.error(f"Research error: {e}", exc_info=True)
            progress_queue.put({
                "step": "error",
                "message": str(e),
                "details": {}
            })
    
    # Start research in background
    research_task = asyncio.create_task(run_research())
    
    async def event_generator():
        try:
            while True:
                try:
                    # Check queue with timeout first (before checking task status)
                    # This ensures we read "completed" message even if task is done
                    try:
                        progress_data = progress_queue.get(timeout=0.5)
                    except thread_queue.Empty:
                        # Queue is empty, check if task is done
                        if research_task.done():
                            # Task completed but no message in queue - check for exception
                            try:
                                research_task.result()
                                # Task completed successfully but no completion message
                                # This shouldn't happen, but handle gracefully
                                yield f"data: {json.dumps({'step': 'error', 'message': 'Research completed unexpectedly', 'details': {}})}\n\n"
                            except Exception as e:
                                yield f"data: {json.dumps({'step': 'error', 'message': str(e), 'details': {}})}\n\n"
                        else:
                            # Send heartbeat to keep connection alive
                            yield f": heartbeat\n\n"
                        continue
                    
                    # Process the progress data
                    try:
                        # Ensure progress_data is serializable
                        serialized_data = {
                            "step": str(progress_data.get("step", "unknown")),
                            "message": str(progress_data.get("message", "")),
                            "details": progress_data.get("details", {})
                        }
                        json_str = json.dumps(serialized_data)
                    except (TypeError, ValueError) as e:
                        logging.error(f"Error serializing progress data: {e}")
                        # Send a safe error message
                        json_str = json.dumps({
                            "step": "error",
                            "message": "Error serializing progress data",
                            "details": {}
                        })
                    
                    if progress_data["step"] == "completed":
                        yield f"data: {json_str}\n\n"
                        break
                    elif progress_data["step"] == "error":
                        yield f"data: {json_str}\n\n"
                        break
                    else:
                        yield f"data: {json_str}\n\n"
                except Exception as e:
                    logging.error(f"Event generator error: {e}", exc_info=True)
                    yield f"data: {json.dumps({'step': 'error', 'message': str(e), 'details': {}})}\n\n"
                    break
        except asyncio.CancelledError:
            # Client disconnected - cancel the research task if possible
            logging.info("Client disconnected, cancelling research task")
            if not research_task.done():
                research_task.cancel()
            raise
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/research")
async def research(request: ResearchRequest):
    """Main research endpoint - provides comprehensive guidance."""
    try:
        vs = get_vector_store()
        agent = ResearchAgent(vs, log_callback=log_callback)
        graph = agent.build_graph()
        
        initial_state = {
            "user_query": request.query,
            "problem_context": request.context or "",
            "research_questions": [],
            "relevant_verses": [],
            "analysis": "",
            "guidance": "",
            "exercises": "",
            "final_answer": ""
        }
        
        result = graph.invoke(initial_state)
        
        return {
            "answer": result["final_answer"],
            "analysis": result["analysis"],
            "guidance": result["guidance"],
            "exercises": result["exercises"],
            "verses": result["relevant_verses"][:10],  # Top 10
            "query": request.query
        }
    except Exception as e:
        logging.error(f"Research error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research/stream")
async def research_stream(request: ResearchRequest):
    """Research endpoint with SSE streaming for progress updates."""
    return await research_with_progress(request)

@app.get("/api/verses")
async def get_verses(chapter: Optional[int] = None, verse_number: Optional[int] = None, verse_id: Optional[str] = None):
    """Get verses from SQLite database."""
    try:
        db_session = get_db_session()
        query = db_session.query(Verse)
        
        if verse_id:
            query = query.filter_by(verse_id=verse_id)
        elif chapter and verse_number:
            query = query.filter_by(chapter=chapter, verse_number=verse_number)
        elif chapter:
            query = query.filter_by(chapter=chapter)
        
        verses = query.all()
        result = [v.to_dict() for v in verses]
        db_session.close()
        
        return {"verses": result, "count": len(result)}
    except Exception as e:
        logging.error(f"Error fetching verses: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/verses/{verse_id}")
async def get_verse_by_id(verse_id: str):
    """Get a specific verse by ID."""
    try:
        db_session = get_db_session()
        verse = db_session.query(Verse).filter_by(verse_id=verse_id).first()
        db_session.close()
        
        if not verse:
            raise HTTPException(status_code=404, detail="Verse not found")
        
        return {"verse": verse.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching verse: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest")
async def ingest_epub(request: IngestionRequest):
    """Ingest Bhagavad Gita EPUB file."""
    global ingestion_status
    
    try:
        ingestion_status = {"status": "processing", "message": "Starting ingestion...", "progress": 10}
        
        vs = get_vector_store()
        service = IngestionService(vs)
        
        epub_path = request.epub_path
        ingestion_status = {"status": "processing", "message": "Processing EPUB file...", "progress": 30}
        
        count = service.ingest_epub(epub_path)
        
        ingestion_status = {
            "status": "completed",
            "message": f"Successfully ingested {count} verses",
            "progress": 100
        }
        
        return ingestion_status
    except FileNotFoundError as e:
        ingestion_status = {"status": "error", "message": str(e), "progress": 0}
        logging.error(f"Ingestion error: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        ingestion_status = {"status": "error", "message": str(e), "progress": 0}
        logging.error(f"Ingestion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ingestion/status")
async def get_ingestion_status():
    """Get ingestion status."""
    return ingestion_status

@app.get("/api/stats")
async def get_stats():
    """Get database statistics."""
    try:
        db_session = get_db_session()
        total_verses = db_session.query(Verse).count()
        chapters = db_session.query(Verse.chapter).distinct().count()
        db_session.close()
        
        vs = get_vector_store()
        collections = vs.client.get_collections()
        vector_count = 0
        for coll in collections.collections:
            if coll.name == vs.collection_name:
                vector_count = vs.client.get_collection(coll.name).points_count
                break
        
        return {
            "total_verses": total_verses,
            "chapters": chapters,
            "vector_store_points": vector_count
        }
    except Exception as e:
        logging.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

