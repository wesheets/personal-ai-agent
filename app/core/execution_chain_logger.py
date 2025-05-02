import os
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ChainStep(BaseModel):
    """Model for a step in an execution chain"""
    chain_id: str
    step_number: int
    agent_name: str
    input_summary: str
    output_summary: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    execution_log_id: Optional[str] = None
    rationale_log_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ExecutionChain(BaseModel):
    """Model for an execution chain"""
    chain_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    steps: List[ChainStep] = Field(default_factory=list)
    status: str = "in_progress"  # in_progress, completed, failed
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ExecutionChainLogger:
    """
    Logger for execution chains in multi-agent workflows
    """
    
    def __init__(self, log_dir: Optional[str] = None):
        # Set up logging directory
        self.log_dir = log_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "execution_chain_logs")
        os.makedirs(self.log_dir, exist_ok=True)
    
    async def create_chain(self, metadata: Optional[Dict[str, Any]] = None) -> ExecutionChain:
        """
        Create a new execution chain
        
        Args:
            metadata: Optional metadata for the chain
            
        Returns:
            New ExecutionChain object
        """
        chain = ExecutionChain(metadata=metadata or {})
        
        # Create directory for this chain
        chain_dir = os.path.join(self.log_dir, chain.chain_id)
        os.makedirs(chain_dir, exist_ok=True)
        
        # Log the initial chain state
        await self._log_chain(chain)
        
        return chain
    
    async def log_step(
        self,
        chain_id: str,
        step_number: int,
        agent_name: str,
        input_text: str,
        output_text: str,
        execution_log_id: Optional[str] = None,
        rationale_log_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChainStep:
        """
        Log a step in an execution chain
        
        Args:
            chain_id: ID of the execution chain
            step_number: Number of this step in the chain
            agent_name: Name of the agent that executed this step
            input_text: Input text for this step
            output_text: Output text from this step
            execution_log_id: ID of the related execution log
            rationale_log_id: ID of the related rationale log
            metadata: Additional metadata for this step
            
        Returns:
            ChainStep object
        """
        # Truncate input and output if too long
        max_length = 500
        input_summary = input_text[:max_length] + "..." if len(input_text) > max_length else input_text
        output_summary = output_text[:max_length] + "..." if len(output_text) > max_length else output_text
        
        # Create the step
        step = ChainStep(
            chain_id=chain_id,
            step_number=step_number,
            agent_name=agent_name,
            input_summary=input_summary,
            output_summary=output_summary,
            execution_log_id=execution_log_id,
            rationale_log_id=rationale_log_id,
            metadata=metadata or {}
        )
        
        # Log the step
        chain_dir = os.path.join(self.log_dir, chain_id)
        os.makedirs(chain_dir, exist_ok=True)
        
        step_file = os.path.join(chain_dir, f"step_{step_number}.json")
        with open(step_file, "w") as f:
            json.dump(step.dict(), f, indent=2)
        
        # Update the chain
        chain = await self.get_chain(chain_id)
        if chain:
            chain.steps.append(step)
            chain.updated_at = datetime.now().isoformat()
            await self._log_chain(chain)
        
        return step
    
    async def complete_chain(self, chain_id: str, status: str = "completed") -> Optional[ExecutionChain]:
        """
        Mark an execution chain as completed
        
        Args:
            chain_id: ID of the execution chain
            status: Final status of the chain (completed or failed)
            
        Returns:
            Updated ExecutionChain object or None if not found
        """
        chain = await self.get_chain(chain_id)
        if not chain:
            return None
        
        chain.status = status
        chain.updated_at = datetime.now().isoformat()
        
        await self._log_chain(chain)
        
        return chain
    
    async def get_chain(self, chain_id: str) -> Optional[ExecutionChain]:
        """
        Get an execution chain by ID
        
        Args:
            chain_id: ID of the execution chain
            
        Returns:
            ExecutionChain object or None if not found
        """
        chain_file = os.path.join(self.log_dir, chain_id, "chain.json")
        
        if not os.path.exists(chain_file):
            return None
        
        with open(chain_file, "r") as f:
            chain_data = json.load(f)
            return ExecutionChain(**chain_data)
    
    async def get_step(self, chain_id: str, step_number: int) -> Optional[ChainStep]:
        """
        Get a step in an execution chain
        
        Args:
            chain_id: ID of the execution chain
            step_number: Number of the step
            
        Returns:
            ChainStep object or None if not found
        """
        step_file = os.path.join(self.log_dir, chain_id, f"step_{step_number}.json")
        
        if not os.path.exists(step_file):
            return None
        
        with open(step_file, "r") as f:
            step_data = json.load(f)
            return ChainStep(**step_data)
    
    async def get_chains(
        self,
        limit: int = 10,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[ExecutionChain]:
        """
        Get execution chains with optional filtering
        
        Args:
            limit: Maximum number of chains to return
            offset: Offset for pagination
            status: Filter by status
            
        Returns:
            List of ExecutionChain objects
        """
        # Get all chain directories
        chain_dirs = [d for d in os.listdir(self.log_dir) if os.path.isdir(os.path.join(self.log_dir, d))]
        
        # Sort by modification time (newest first)
        chain_dirs.sort(key=lambda d: os.path.getmtime(os.path.join(self.log_dir, d, "chain.json")) if os.path.exists(os.path.join(self.log_dir, d, "chain.json")) else 0, reverse=True)
        
        # Apply pagination
        chain_dirs = chain_dirs[offset:offset + limit]
        
        # Load chains
        chains = []
        for chain_id in chain_dirs:
            chain = await self.get_chain(chain_id)
            if chain and (status is None or chain.status == status):
                chains.append(chain)
        
        return chains
    
    async def _log_chain(self, chain: ExecutionChain) -> None:
        """
        Log an execution chain
        
        Args:
            chain: ExecutionChain object to log
        """
        chain_dir = os.path.join(self.log_dir, chain.chain_id)
        os.makedirs(chain_dir, exist_ok=True)
        
        chain_file = os.path.join(chain_dir, "chain.json")
        with open(chain_file, "w") as f:
            json.dump(chain.dict(), f, indent=2)

# Singleton instance
_execution_chain_logger = None

def get_execution_chain_logger() -> ExecutionChainLogger:
    """
    Get the singleton ExecutionChainLogger instance
    """
    global _execution_chain_logger
    if _execution_chain_logger is None:
        _execution_chain_logger = ExecutionChainLogger()
    return _execution_chain_logger
