import os
from typing import Optional, Dict, Any
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseConfig:
    """Configuration for database connections"""
    
    def __init__(self):
        self.db_type = os.getenv("DB_TYPE", "local")  # "local" or "supabase"
        
        # Supabase configuration
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        # Local database configuration
        self.local_db_path = os.getenv("LOCAL_DB_PATH", os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "db"
        ))
        
    def get_config(self) -> Dict[str, Any]:
        """Get the database configuration"""
        if self.db_type == "supabase":
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("Supabase URL and key must be provided in environment variables")
            
            return {
                "type": "supabase",
                "url": self.supabase_url,
                "key": self.supabase_key
            }
        else:
            # Ensure the local database directory exists
            os.makedirs(self.local_db_path, exist_ok=True)
            
            return {
                "type": "local",
                "path": self.local_db_path
            }

class Database:
    """Base database interface"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def connect(self):
        """Connect to the database"""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def disconnect(self):
        """Disconnect from the database"""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def store(self, collection: str, data: Dict[str, Any]) -> str:
        """Store data in the database"""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def query(self, collection: str, query: Dict[str, Any], limit: int = 10) -> list:
        """Query data from the database"""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def get(self, collection: str, id: str) -> Optional[Dict[str, Any]]:
        """Get a specific item from the database"""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def update(self, collection: str, id: str, data: Dict[str, Any]) -> bool:
        """Update an item in the database"""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def delete(self, collection: str, id: str) -> bool:
        """Delete an item from the database"""
        raise NotImplementedError("Subclasses must implement this method")

class LocalDatabase(Database):
    """Local file-based database implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.db_path = config["path"]
        self.collections = {}
    
    async def connect(self):
        """Connect to the local database (load files)"""
        # Create the database directory if it doesn't exist
        os.makedirs(self.db_path, exist_ok=True)
        
        # Load all collection files
        for filename in os.listdir(self.db_path):
            if filename.endswith(".json"):
                collection_name = filename[:-5]  # Remove .json extension
                collection_path = os.path.join(self.db_path, filename)
                
                try:
                    with open(collection_path, 'r') as f:
                        self.collections[collection_name] = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    # Initialize with empty list if file is empty or doesn't exist
                    self.collections[collection_name] = []
    
    async def disconnect(self):
        """Disconnect from the local database (save files)"""
        # Save all collections to files
        for collection_name, data in self.collections.items():
            collection_path = os.path.join(self.db_path, f"{collection_name}.json")
            
            with open(collection_path, 'w') as f:
                json.dump(data, f, indent=2)
    
    def _get_collection(self, collection: str) -> list:
        """Get or create a collection"""
        if collection not in self.collections:
            self.collections[collection] = []
        
        return self.collections[collection]
    
    async def store(self, collection: str, data: Dict[str, Any]) -> str:
        """Store data in the local database"""
        collection_data = self._get_collection(collection)
        
        # Ensure the data has an ID
        if "id" not in data:
            import uuid
            data["id"] = str(uuid.uuid4())
        
        collection_data.append(data)
        
        # Save the collection to file
        collection_path = os.path.join(self.db_path, f"{collection}.json")
        with open(collection_path, 'w') as f:
            json.dump(collection_data, f, indent=2)
        
        return data["id"]
    
    async def query(self, collection: str, query: Dict[str, Any], limit: int = 10) -> list:
        """Query data from the local database"""
        collection_data = self._get_collection(collection)
        
        # Simple filtering based on query parameters
        results = []
        for item in collection_data:
            match = True
            for key, value in query.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            
            if match:
                results.append(item)
                
                if len(results) >= limit:
                    break
        
        return results
    
    async def get(self, collection: str, id: str) -> Optional[Dict[str, Any]]:
        """Get a specific item from the local database"""
        collection_data = self._get_collection(collection)
        
        for item in collection_data:
            if item.get("id") == id:
                return item
        
        return None
    
    async def update(self, collection: str, id: str, data: Dict[str, Any]) -> bool:
        """Update an item in the local database"""
        collection_data = self._get_collection(collection)
        
        for i, item in enumerate(collection_data):
            if item.get("id") == id:
                # Update the item with new data
                collection_data[i] = {**item, **data}
                
                # Save the collection to file
                collection_path = os.path.join(self.db_path, f"{collection}.json")
                with open(collection_path, 'w') as f:
                    json.dump(collection_data, f, indent=2)
                
                return True
        
        return False
    
    async def delete(self, collection: str, id: str) -> bool:
        """Delete an item from the local database"""
        collection_data = self._get_collection(collection)
        
        for i, item in enumerate(collection_data):
            if item.get("id") == id:
                # Remove the item
                del collection_data[i]
                
                # Save the collection to file
                collection_path = os.path.join(self.db_path, f"{collection}.json")
                with open(collection_path, 'w') as f:
                    json.dump(collection_data, f, indent=2)
                
                return True
        
        return False

# Factory function to get the appropriate database implementation
async def get_database():
    """Get a database instance based on configuration"""
    config = DatabaseConfig().get_config()
    
    if config["type"] == "supabase":
        # This would be implemented with actual Supabase integration
        # For now, we'll use the local database as a placeholder
        db = LocalDatabase(config)
    else:
        db = LocalDatabase(config)
    
    await db.connect()
    return db
