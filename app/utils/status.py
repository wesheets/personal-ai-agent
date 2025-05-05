"""
Defines status codes for agent operations.
"""

from enum import Enum

class ResultStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    REJECTED = "rejected"
    # Add more statuses as needed

