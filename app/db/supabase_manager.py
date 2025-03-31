import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseManager:
    """
    Manager for Supabase connection and operations
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("WARNING: SUPABASE_URL and SUPABASE_KEY not set. Using mock client for testing.")
            # Create a mock client for testing purposes
            from unittest.mock import MagicMock
            self.client = MagicMock()
            self.client.table.return_value.select.return_value.execute.return_value.data = []
            self.client.table.return_value.insert.return_value.execute.return_value.data = [{"id": "mock-id-123"}]
            self.client.rpc.return_value.execute.return_value.data = []
            self.is_connected = False
        else:
            # Initialize real Supabase client
            self.client = create_client(supabase_url, supabase_key)
            self.is_connected = True
    
    def get_client(self) -> Client:
        """Get the Supabase client instance"""
        return self.client
    
    async def check_connection(self) -> bool:
        """Check if the connection to Supabase is working"""
        try:
            # Simple query to check connection
            self.client.table("agent_memories").select("id").limit(1).execute()
            return True
        except Exception as e:
            print(f"Supabase connection error: {str(e)}")
            return False
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Get information about the database"""
        try:
            # This is a simplified approach
            # In a real implementation, you would query Supabase for actual stats
            memory_count = len(self.client.table("agent_memories").select("id").execute().data)
            
            return {
                "status": "connected",
                "memory_count": memory_count,
                "database_type": "Supabase with pgvector"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

def get_supabase_client() -> Client:
    """
    Dependency to get the Supabase client
    """
    manager = SupabaseManager()
    return manager.get_client()
