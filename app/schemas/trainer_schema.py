"""
TRAINER Agent Schema Definitions

This module defines the schemas for TRAINER agent requests and responses.
The TRAINER agent is responsible for training models, fine-tuning parameters,
and evaluating model performance.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class TrainerTaskRequest(BaseModel):
    """
    Schema for TRAINER agent task request.
    """
    task: str = Field(..., description="Task to perform (e.g., 'train', 'evaluate', 'fine-tune')")
    model_id: str = Field(..., description="Identifier for the model to train or evaluate")
    project_id: Optional[str] = Field(None, description="Project identifier if applicable")
    dataset_id: Optional[str] = Field(None, description="Dataset identifier if applicable")
    parameters: Optional[Dict[str, Any]] = Field(
        default={},
        description="Training parameters (e.g., epochs, batch_size, learning_rate)"
    )
    tools: Optional[List[str]] = Field(
        default=["train", "evaluate", "fine_tune"],
        description="List of tools to use for the training task"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "task": "train",
                "model_id": "model_123",
                "project_id": "proj_456",
                "dataset_id": "dataset_789",
                "parameters": {
                    "epochs": 10,
                    "batch_size": 32,
                    "learning_rate": 0.001
                },
                "tools": ["train", "evaluate"]
            }
        }

class TrainingMetrics(BaseModel):
    """
    Schema for training metrics.
    """
    accuracy: float = Field(..., description="Model accuracy")
    loss: float = Field(..., description="Training loss")
    precision: Optional[float] = Field(None, description="Precision score")
    recall: Optional[float] = Field(None, description="Recall score")
    f1_score: Optional[float] = Field(None, description="F1 score")
    training_time: float = Field(..., description="Training time in seconds")
    epochs_completed: int = Field(..., description="Number of epochs completed")
    
    class Config:
        schema_extra = {
            "example": {
                "accuracy": 0.92,
                "loss": 0.08,
                "precision": 0.91,
                "recall": 0.89,
                "f1_score": 0.90,
                "training_time": 3600,
                "epochs_completed": 10
            }
        }

class ModelInfo(BaseModel):
    """
    Schema for model information.
    """
    model_id: str = Field(..., description="Model identifier")
    model_type: str = Field(..., description="Type of model (e.g., 'classification', 'regression')")
    parameters: Dict[str, Any] = Field(..., description="Model parameters")
    size: int = Field(..., description="Model size in bytes")
    created_at: str = Field(..., description="Creation timestamp")
    version: str = Field(..., description="Model version")
    
    class Config:
        schema_extra = {
            "example": {
                "model_id": "model_123",
                "model_type": "classification",
                "parameters": {
                    "layers": 5,
                    "hidden_units": 128,
                    "activation": "relu"
                },
                "size": 5242880,
                "created_at": "2025-04-24T18:51:28.123456",
                "version": "1.0.0"
            }
        }

class TrainerTaskResult(BaseModel):
    """
    Schema for TRAINER agent task result.
    """
    status: str = Field(..., description="Status of the task (success, error)")
    message: str = Field(..., description="Message describing the result")
    task: str = Field(..., description="Task that was performed")
    model_id: str = Field(..., description="Model identifier")
    project_id: Optional[str] = Field(None, description="Project identifier if applicable")
    dataset_id: Optional[str] = Field(None, description="Dataset identifier if applicable")
    metrics: Optional[TrainingMetrics] = Field(None, description="Training metrics if applicable")
    model_info: Optional[ModelInfo] = Field(None, description="Model information if applicable")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations for improving the model")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the task"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Model trained successfully",
                "task": "train",
                "model_id": "model_123",
                "project_id": "proj_456",
                "dataset_id": "dataset_789",
                "metrics": {
                    "accuracy": 0.92,
                    "loss": 0.08,
                    "precision": 0.91,
                    "recall": 0.89,
                    "f1_score": 0.90,
                    "training_time": 3600,
                    "epochs_completed": 10
                },
                "model_info": {
                    "model_id": "model_123",
                    "model_type": "classification",
                    "parameters": {
                        "layers": 5,
                        "hidden_units": 128,
                        "activation": "relu"
                    },
                    "size": 5242880,
                    "created_at": "2025-04-24T18:51:28.123456",
                    "version": "1.0.0"
                },
                "recommendations": [
                    "Increase batch size for faster training",
                    "Try different learning rates",
                    "Add more data for improved accuracy"
                ],
                "timestamp": "2025-04-24T18:51:28.123456"
            }
        }

class TrainerErrorResult(BaseModel):
    """
    Schema for TRAINER agent error result.
    """
    status: str = Field("error", description="Status of the operation")
    message: str = Field(..., description="Error message")
    task: Optional[str] = Field(None, description="Task that was attempted")
    model_id: Optional[str] = Field(None, description="Model identifier if applicable")
    project_id: Optional[str] = Field(None, description="Project identifier if applicable")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
