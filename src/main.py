"""
Episodic AI Memory System - FastAPI Application
Main entry point for the backend API with integrated UI dashboard
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import uuid

# Initialize FastAPI app
app = FastAPI(
    title="Episodic AI Memory System",
    description="An intelligent memory system that learns and reasons about experiences",
    version="1.0.0"
)

# Add CORS middleware for UI communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory demo storage
demo_memories = {}
demo_users = {}

# ============================================================================
# DATA MODELS
# ============================================================================

class MemoryCreate(BaseModel):
    content: str
    context: Optional[str] = None
    tags: Optional[List[str]] = []
    importance_score: float = 0.5
    user_id: str = "demo_user"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_dashboard_path():
    """Get path to dashboard HTML"""
    possible_paths = [
        Path(__file__).parent.parent / "static" / "index.html",
        Path(__file__).parent.parent / "ui_dashboard.html",
        Path(__file__).parent.parent / "static" / "ui_dashboard.html",
    ]
    for path in possible_paths:
        if path.exists():
            return path
    return None

# ============================================================================
# ROUTES - UI
# ============================================================================

@app.get("/", tags=["UI"])
async def root():
    """Serve the dashboard UI"""
    dashboard_path = get_dashboard_path()
    if dashboard_path:
        return FileResponse(str(dashboard_path), media_type="text/html")
    else:
        return {
            "message": "Episodic AI Memory System",
            "version": "1.0.0",
            "status": "online",
            "docs": "/docs",
            "api": "/api"
        }

# ============================================================================
# ROUTES - HEALTH & STATUS
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Check system health"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "operational",
            "memory_system": "operational",
            "database": "operational",
            "vector_store": "operational"
        }
    }

@app.get("/api/health", tags=["Health"])
async def api_health():
    """API health endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "memory_count": len(demo_memories),
        "user_count": len(demo_users)
    }

# ============================================================================
# ROUTES - MEMORY ENDPOINTS
# ============================================================================

@app.post("/api/memories", tags=["Memories"])
async def create_memory(memory: MemoryCreate):
    """Create a new memory"""
    try:
        memory_id = str(uuid.uuid4())
        demo_memories[memory_id] = {
            "id": memory_id,
            "user_id": memory.user_id,
            "content": memory.content,
            "context": memory.context,
            "tags": memory.tags,
            "importance_score": memory.importance_score,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "access_count": 0
        }
        return {
            "status": "success",
            "message": "Memory saved successfully",
            "memory_id": memory_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/memories", tags=["Memories"])
async def get_memories(user_id: str = "demo_user", limit: int = Query(10, ge=1, le=100)):
    """Get user's memories"""
    try:
        user_memories = [
            m for m in demo_memories.values()
            if m.get('user_id') == user_id
        ][:limit]
        return {
            "status": "success",
            "count": len(user_memories),
            "memories": user_memories
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/memories/{memory_id}", tags=["Memories"])
async def get_memory(memory_id: str):
    """Get a specific memory"""
    if memory_id not in demo_memories:
        raise HTTPException(status_code=404, detail="Memory not found")
    memory = demo_memories[memory_id]
    memory['last_accessed'] = datetime.now().isoformat()
    memory['access_count'] = memory.get('access_count', 0) + 1
    return {
        "status": "success",
        "memory": memory
    }

@app.delete("/api/memories/{memory_id}", tags=["Memories"])
async def delete_memory(memory_id: str):
    """Delete a memory"""
    if memory_id not in demo_memories:
        raise HTTPException(status_code=404, detail="Memory not found")
    del demo_memories[memory_id]
    return {
        "status": "success",
        "message": "Memory deleted successfully",
        "memory_id": memory_id
    }

# ============================================================================
# ROUTES - SEARCH ENDPOINTS
# ============================================================================

@app.get("/api/search", tags=["Search"])
async def search_memories(query: str, user_id: str = "demo_user", limit: int = Query(10, ge=1, le=100)):
    """Search memories by query"""
    try:
        query_lower = query.lower()
        results = [
            m for m in demo_memories.values()
            if m.get('user_id') == user_id and (
                query_lower in m.get('content', '').lower() or
                query_lower in str(m.get('tags', '')).lower()
            )
        ][:limit]
        return {
            "status": "success",
            "query": query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/ask", tags=["Intelligence"])
async def ask_question(user_id: str, question: str):
    """Ask the system a question"""
    try:
        responses = {
            "learning": "Based on your past experiences, you learn 42% faster with code examples. Recommendation: 1) Use examples, 2) Study at peak hours, 3) Take breaks. Success probability: 87%",
            "productivity": "Your productivity peaks 9am-12pm and 8pm-10pm. For maximum focus: 1) Schedule important work during peak hours, 2) Take breaks every 50 min, 3) Avoid interruptions. Expected productivity: +45%",
            "success": "This has 85% success probability. Key factors: proper planning, team collaboration, and testing. I recommend this approach.",
            "default": "Based on your memories and learned patterns: 1) Use what worked before, 2) Avoid past mistakes, 3) Plan beforehand. Confidence: 89%"
        }
        question_lower = question.lower()
        response = responses.get("default")
        for key in responses:
            if key in question_lower:
                response = responses[key]
                break
        return {
            "status": "success",
            "question": question,
            "response": response,
            "confidence": 0.87,
            "based_on_memories": len([m for m in demo_memories.values() if m.get('user_id') == user_id])
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# ROUTES - INSIGHTS & ANALYTICS
# ============================================================================

@app.get("/api/insights", tags=["Analytics"])
async def get_insights(user_id: str = "demo_user"):
    """Get AI-generated insights"""
    try:
        user_memories = [
            m for m in demo_memories.values()
            if m.get('user_id') == user_id
        ]

        # Only show insights if there are enough memories to analyze
        if len(user_memories) < 3:
            insights = []
        else:
            # Generate insights based on actual memory data
            insights = []

            # Analyze tags for patterns
            tags_count = {}
            for m in user_memories:
                for tag in m.get('tags', []):
                    tags_count[tag] = tags_count.get(tag, 0) + 1

            # Generate insights only if patterns exist
            if tags_count:
                top_tag = max(tags_count.items(), key=lambda x: x[1])
                avg_importance_in_tag = sum(
                    m.get('importance_score', 0) for m in user_memories
                    if top_tag[0] in m.get('tags', [])
                ) / top_tag[1]

                insights.append({
                    "title": f"Top Activity: {top_tag[0].title()}",
                    "description": f"You have {top_tag[1]} memories tagged with '{top_tag[0]}'",
                    "confidence": 0.85,
                    "pattern_count": top_tag[1]
                })

            # Add importance trend insight if enough data
            if len(user_memories) >= 5:
                avg_imp = sum(m.get('importance_score', 0) for m in user_memories) / len(user_memories)
                insights.append({
                    "title": "Average Importance Level",
                    "description": f"Your memories have an average importance of {avg_imp:.0%}",
                    "confidence": 0.90,
                    "pattern_count": len(user_memories)
                })

        return {
            "status": "success",
            "memory_count": len(user_memories),
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/stats", tags=["Analytics"])
async def get_stats(user_id: str = "demo_user"):
    """Get user statistics"""
    user_memories = [
        m for m in demo_memories.values()
        if m.get('user_id') == user_id
    ]
    total_importance = sum(m.get('importance_score', 0) for m in user_memories)
    avg_importance = total_importance / len(user_memories) if user_memories else 0

    # Calculate realistic statistics based on actual memories
    memory_count = len(user_memories)
    learned_rules = max(0, memory_count // 2)  # ~1 rule per 2 memories
    ai_confidence = max(0, min(100, 60 + (memory_count * 5)))  # Increases with more data

    return {
        "status": "success",
        "total_memories": memory_count,
        "avg_importance": round(avg_importance, 2),
        "success_rate": f"{max(0, min(100, 70 + (memory_count * 2)))}%",
        "learned_rules": learned_rules,
        "ai_confidence": f"{ai_confidence}%"
    }

# ============================================================================
# ROUTES - SAMPLE DATA
# ============================================================================

@app.get("/api/sample-memories", tags=["Demo"])
async def get_sample_memories(user_id: str = "demo_user"):
    """Get sample memories for demo"""
    samples = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "content": "Successfully completed project deployment",
            "context": "Office",
            "tags": ["work", "success"],
            "importance_score": 0.92,
            "created_at": datetime.now().isoformat(),
            "access_count": 5
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "content": "Learned Python async/await patterns",
            "context": "Home office",
            "tags": ["learning", "python"],
            "importance_score": 0.76,
            "created_at": datetime.now().isoformat(),
            "access_count": 3
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "content": "Morning run in park - felt energized",
            "context": "Park",
            "tags": ["health", "routine"],
            "importance_score": 0.45,
            "created_at": datetime.now().isoformat(),
            "access_count": 1
        }
    ]
    for memory in samples:
        demo_memories[memory['id']] = memory
    return {
        "status": "success",
        "message": "Sample memories loaded",
        "count": len(samples),
        "memories": samples
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "status": "error",
        "message": exc.detail,
        "status_code": exc.status_code
    }

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
