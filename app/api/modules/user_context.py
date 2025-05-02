"""
User Context Module

This module provides REST API endpoints for registering users, assigning memory scopes,
and supporting multi-user agent personalization.

Key features:
- User registration with preferences
- Memory scoping for per-user memory threads
- Agent personalization (tone, mode, persona)
- Contextual scoping of all actions (write, read, reflect, audit)
"""

import os
import json
import uuid
import sqlite3
from datetime import datetime
import logging
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse

# Import models
from app.api.modules.user_context_models import (
    UserContextRegisterRequest,
    UserContextRegisterResponse,
    UserContextGetRequest,
    UserContextGetResponse
)

# Configure logging
logger = logging.getLogger("api.modules.user_context")

# Create router
router = APIRouter()
print("🧠 Route defined: /api/modules/user_context -> user_context_module")

# Path for SQLite database file
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "db")
DB_FILE = os.path.join(DB_DIR, "memory.db")

# In-memory store for user contexts (backed by SQLite)
user_context_store = {}

# Initialize user context store from database
def initialize_user_context_store():
    """Initialize the user context store from SQLite database"""
    try:
        # Ensure the user_contexts table exists
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Create user_contexts table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_contexts (
                user_context_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                preferences TEXT NOT NULL,  -- Stored as JSON
                memory_scope TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for common query patterns
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_contexts_user_id ON user_contexts(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_contexts_agent_id ON user_contexts(agent_id)")
        
        conn.commit()
        
        # Load existing user contexts
        cursor.execute("SELECT * FROM user_contexts")
        rows = cursor.fetchall()
        
        # Convert rows to dictionaries and add to in-memory store
        for row in rows:
            user_context = dict(row)
            # Parse preferences from JSON string
            user_context["preferences"] = json.loads(user_context["preferences"])
            user_context_store[user_context["user_id"]] = user_context
        
        print(f"🧠 [INIT] Loaded {len(user_context_store)} user contexts from database")
        conn.close()
        return len(user_context_store)
    except Exception as e:
        logger.error(f"❌ Error initializing user context store: {str(e)}")
        print(f"❌ [INIT] Error loading user contexts: {str(e)}")
        return 0

# Initialize store on module import
initialized_count = initialize_user_context_store()
logger.info(f"🧠 User context module loaded with {initialized_count} contexts from database")

def write_user_context(user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Write a user context to both the SQLite database and in-memory store
    
    Args:
        user_context: Dictionary containing user context data
        
    Returns:
        The user context with its user_context_id
    """
    try:
        # Convert preferences to JSON string
        preferences_json = json.dumps(user_context.get("preferences", {}))
        
        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Insert or replace the user context in the database
        cursor.execute("""
            INSERT OR REPLACE INTO user_contexts (
                user_context_id, user_id, name, agent_id, preferences, memory_scope, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_context["user_context_id"],
            user_context["user_id"],
            user_context["name"],
            user_context["agent_id"],
            preferences_json,
            user_context["memory_scope"],
            user_context.get("created_at", datetime.utcnow().isoformat())
        ))
        
        conn.commit()
        conn.close()
        
        # Add to in-memory store
        user_context_store[user_context["user_id"]] = user_context
        
        logger.info(f"✅ User context written for {user_context['user_id']}: {user_context['user_context_id']}")
        print(f"💾 [DB] User context written: {user_context['user_context_id']} (user: {user_context['user_id']})")
        return user_context
    except Exception as e:
        logger.error(f"❌ Error writing user context: {str(e)}")
        print(f"❌ [DB] Error writing user context: {str(e)}")
        raise

def read_user_context(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Read a user context from the store or database
    
    Args:
        user_id: The ID of the user to read
        
    Returns:
        The user context as a dictionary, or None if not found
    """
    try:
        # Check in-memory store first
        if user_id in user_context_store:
            logger.info(f"✅ User context found in memory store: {user_id}")
            return user_context_store[user_id]
        
        # If not in memory, check database
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM user_contexts WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row:
            logger.info(f"⚠️ User context not found: {user_id}")
            return None
        
        # Convert row to dictionary
        user_context = dict(row)
        
        # Parse preferences from JSON string
        user_context["preferences"] = json.loads(user_context["preferences"])
        
        # Add to in-memory store for future access
        user_context_store[user_id] = user_context
        
        conn.close()
        logger.info(f"✅ User context retrieved from database: {user_id}")
        return user_context
    except Exception as e:
        logger.error(f"❌ Error reading user context: {str(e)}")
        return None

@router.post("/register")
async def register_user(request: Request):
    """
    Register a new user and return their unique memory scope
    
    This endpoint creates a new user context with the provided information,
    generates a unique user_context_id and memory_scope, and stores the context
    in both the database and in-memory store.
    
    Request body:
    - user_id: Unique identifier for the user
    - name: User's name
    - agent_id: ID of the agent associated with this user
    - preferences: Dictionary of user preferences (optional)
    
    Returns:
    - status: "ok" if successful
    - user_context_id: Unique identifier for the user context
    - memory_scope: Memory scope for this user (format: "user:{user_id}")
    """
    try:
        # Parse request body
        body = await request.json()
        register_request = UserContextRegisterRequest(**body)
        
        # Check if user already exists
        existing_user = read_user_context(register_request.user_id)
        if existing_user:
            logger.info(f"⚠️ User already exists, updating: {register_request.user_id}")
        
        # Generate user_context_id if new user
        user_context_id = f"ctx_{register_request.user_id}"
        
        # Generate memory scope
        memory_scope = f"user:{register_request.user_id}"
        
        # Create default preferences if none provided
        preferences = register_request.preferences
        if not preferences:
            preferences = {
                "mode": "standard",
                "persona": "default"
            }
        
        # Create user context
        user_context = {
            "user_context_id": user_context_id,
            "user_id": register_request.user_id,
            "name": register_request.name,
            "agent_id": register_request.agent_id,
            "preferences": preferences,
            "memory_scope": memory_scope,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Write to database and in-memory store
        write_user_context(user_context)
        
        # Create response
        response = UserContextRegisterResponse(
            status="ok",
            user_context_id=user_context_id,
            memory_scope=memory_scope
        )
        
        return response.dict()
    except Exception as e:
        logger.error(f"❌ Error registering user: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to register user: {str(e)}"
            }
        )

@router.get("/get")
async def get_user_context(user_id: str = Query(..., description="ID of the user to retrieve context for")):
    """
    Return the user's current context metadata
    
    This endpoint retrieves the user context for the specified user_id,
    including their preferences, associated agent, and memory scope.
    
    Query parameters:
    - user_id: ID of the user to retrieve context for
    
    Returns:
    - user_id: ID of the user
    - agent_id: ID of the associated agent
    - memory_scope: Memory scope for this user
    - preferences: Dictionary of user preferences
    - created_at: Timestamp when the user context was created
    """
    try:
        # Read user context
        user_context = read_user_context(user_id)
        
        if not user_context:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"User context not found for user_id: {user_id}"
                }
            )
        
        # Create response
        response = UserContextGetResponse(
            user_id=user_context["user_id"],
            agent_id=user_context["agent_id"],
            memory_scope=user_context["memory_scope"],
            preferences=user_context["preferences"],
            created_at=user_context.get("created_at")
        )
        
        return response.dict()
    except Exception as e:
        logger.error(f"❌ Error retrieving user context: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to retrieve user context: {str(e)}"
            }
        )

@router.post("/update")
async def update_user_context(request: Request):
    """
    Update user context with provided data
    
    This endpoint updates the user context with the provided information.
    It's a simplified version of the register endpoint for quick updates.
    
    Request body:
    - user_id: Unique identifier for the user (required)
    - agent_id: ID of the agent associated with this user (optional)
    - memory_scope: Memory scope for this user (optional)
    - preferences: Dictionary of user preferences (optional)
    
    Returns:
    - status: "ok" if successful
    - message: Confirmation message
    """
    try:
        # Parse request body
        body = await request.json()
        user_id = body.get("user_id")
        
        if not user_id:
            return JSONResponse(
                status_code=400, 
                content={"status": "error", "message": "user_id is required"}
            )
        
        # Check if user already exists
        existing_user = read_user_context(user_id)
        
        # If user exists, update their context
        if existing_user:
            # Update fields that are provided
            if "agent_id" in body:
                existing_user["agent_id"] = body["agent_id"]
            
            if "memory_scope" in body:
                existing_user["memory_scope"] = body["memory_scope"]
            
            if "preferences" in body:
                existing_user["preferences"] = body["preferences"]
            
            # Write updated context
            write_user_context(existing_user)
            logger.info(f"✅ Updated existing user context: {user_id}")
        else:
            # For new users, create a minimal context
            user_context_id = f"ctx_{user_id}"
            memory_scope = body.get("memory_scope", f"user:{user_id}")
            agent_id = body.get("agent_id", "hal")  # Default to HAL if not specified
            
            # Create user context
            user_context = {
                "user_context_id": user_context_id,
                "user_id": user_id,
                "name": f"User {user_id}",  # Default name
                "agent_id": agent_id,
                "preferences": body.get("preferences", {}),
                "memory_scope": memory_scope,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Write to database and in-memory store
            write_user_context(user_context)
            logger.info(f"✅ Created new user context via update endpoint: {user_id}")
        
        # Store the full context in the in-memory store for quick access
        user_context_store[user_id] = body
        
        return {"status": "ok", "message": f"Context stored for {user_id}"}
    except Exception as e:
        logger.error(f"❌ Error updating user context: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to update user context: {str(e)}"
            }
        )
