"""
Tests for the enhanced Belief Versioning module.

This module tests the new features added to the Belief Versioning module:
- Semantic versioning
- Conflict resolution
- Belief dependency tracking
- Change impact analysis
- Branching and merging
"""

import os
import json
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

from app.modules.belief_versioning import (
    BeliefVersionManager,
    SemanticVersion,
    BeliefLock,
    get_belief_version_manager
)

# Test data
TEST_BELIEF_ID = "test_belief_123"
TEST_AUTHOR = "test_user"

@pytest.fixture
def belief_version_manager():
    """Create a belief version manager instance for testing."""
    with patch('app.modules.belief_versioning.read_from_memory') as mock_read, \
         patch('app.modules.belief_versioning.write_to_memory') as mock_write:
        
        # Mock read_from_memory to return test data
        async def mock_read_impl(key):
            if key == f"belief_version[{TEST_BELIEF_ID}][main]":
                return {
                    "belief_id": TEST_BELIEF_ID,
                    "version": 1,
                    "semantic_version": {"major": 1, "minor": 0, "patch": 0},
                    "text": "This is a test belief",
                    "author": "system",
                    "timestamp": datetime.utcnow().isoformat(),
                    "previous_version": None,
                    "change_type": "creation",
                    "change_summary": "Initial creation of belief",
                    "branch": "main"
                }
            elif key == f"belief_versions[{TEST_BELIEF_ID}][main]":
                return [
                    {
                        "belief_id": TEST_BELIEF_ID,
                        "version": 1,
                        "semantic_version": {"major": 1, "minor": 0, "patch": 0},
                        "text": "This is a test belief",
                        "author": "system",
                        "timestamp": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                        "previous_version": None,
                        "change_type": "creation",
                        "change_summary": "Initial creation of belief",
                        "branch": "main"
                    }
                ]
            elif key == f"belief_dependencies[{TEST_BELIEF_ID}]":
                return {
                    "depends_on": ["belief_123", "belief_456"],
                    "depended_by": ["belief_789"]
                }
            elif key == f"belief_locks[{TEST_BELIEF_ID}]":
                return []
            elif key == f"belief_branches[{TEST_BELIEF_ID}]":
                return {
                    "main": {
                        "head": 1,
                        "locked": False
                    }
                }
            return None
        
        mock_read.side_effect = mock_read_impl
        mock_write.return_value = True
        
        manager = BeliefVersionManager()
        yield manager

class TestSemanticVersion:
    """Tests for the SemanticVersion class."""
    
    def test_semantic_version_creation(self):
        """Test creating semantic versions."""
        # Default version
        version = SemanticVersion()
        assert version.major == 1
        assert version.minor == 0
        assert version.patch == 0
        assert str(version) == "1.0.0"
        
        # Custom version
        version = SemanticVersion(2, 3, 4)
        assert version.major == 2
        assert version.minor == 3
        assert version.patch == 4
        assert str(version) == "2.3.4"
    
    def test_semantic_version_from_string(self):
        """Test creating semantic versions from strings."""
        # Full version string
        version = SemanticVersion.from_string("2.3.4")
        assert version.major == 2
        assert version.minor == 3
        assert version.patch == 4
        
        # Partial version string
        version = SemanticVersion.from_string("2.3")
        assert version.major == 2
        assert version.minor == 3
        assert version.patch == 0
        
        # Major only
        version = SemanticVersion.from_string("2")
        assert version.major == 2
        assert version.minor == 0
        assert version.patch == 0
    
    def test_semantic_version_from_change_type(self):
        """Test creating semantic versions based on change types."""
        base_version = SemanticVersion(1, 2, 3)
        
        # Major change
        new_version = SemanticVersion.from_change_type(base_version, "major")
        assert new_version.major == 2
        assert new_version.minor == 0
        assert new_version.patch == 0
        
        # Minor change
        new_version = SemanticVersion.from_change_type(base_version, "minor")
        assert new_version.major == 1
        assert new_version.minor == 3
        assert new_version.patch == 0
        
        # Patch change
        new_version = SemanticVersion.from_change_type(base_version, "patch")
        assert new_version.major == 1
        assert new_version.minor == 2
        assert new_version.patch == 4
        
        # Unknown change type (defaults to patch)
        new_version = SemanticVersion.from_change_type(base_version, "unknown")
        assert new_version.major == 1
        assert new_version.minor == 2
        assert new_version.patch == 4
        
        # Initial version (no previous version)
        new_version = SemanticVersion.from_change_type(None, "major")
        assert new_version.major == 1
        assert new_version.minor == 0
        assert new_version.patch == 0
    
    def test_semantic_version_comparison(self):
        """Test comparing semantic versions."""
        v1 = SemanticVersion(1, 0, 0)
        v2 = SemanticVersion(1, 0, 0)
        v3 = SemanticVersion(1, 0, 1)
        v4 = SemanticVersion(1, 1, 0)
        v5 = SemanticVersion(2, 0, 0)
        
        # Equality
        assert v1 == v2
        assert not (v1 == v3)
        
        # Less than
        assert v1 < v3
        assert v3 < v4
        assert v4 < v5
        assert not (v5 < v4)
        
        # Greater than
        assert v5 > v4
        assert v4 > v3
        assert v3 > v1
        assert not (v1 > v3)
    
    def test_semantic_version_dict_conversion(self):
        """Test converting semantic versions to and from dictionaries."""
        version = SemanticVersion(2, 3, 4)
        
        # To dictionary
        version_dict = version.to_dict()
        assert version_dict == {"major": 2, "minor": 3, "patch": 4}
        
        # From dictionary
        new_version = SemanticVersion.from_dict(version_dict)
        assert new_version == version
        assert new_version.major == 2
        assert new_version.minor == 3
        assert new_version.patch == 4

class TestBeliefLock:
    """Tests for the BeliefLock class."""
    
    def test_belief_lock_creation(self):
        """Test creating belief locks."""
        # Default lock (exclusive)
        lock = BeliefLock(TEST_BELIEF_ID, TEST_AUTHOR)
        assert lock.belief_id == TEST_BELIEF_ID
        assert lock.owner == TEST_AUTHOR
        assert lock.lock_type == "exclusive"
        assert not lock.is_expired()
        
        # Shared lock
        lock = BeliefLock(TEST_BELIEF_ID, TEST_AUTHOR, "shared")
        assert lock.lock_type == "shared"
        
        # Custom expiration
        expiration = datetime.utcnow() + timedelta(minutes=10)
        lock = BeliefLock(TEST_BELIEF_ID, TEST_AUTHOR, expiration=expiration)
        assert lock.expiration == expiration
    
    def test_belief_lock_expiration(self):
        """Test belief lock expiration."""
        # Expired lock
        expiration = datetime.utcnow() - timedelta(seconds=1)
        lock = BeliefLock(TEST_BELIEF_ID, TEST_AUTHOR, expiration=expiration)
        assert lock.is_expired()
        
        # Non-expired lock
        expiration = datetime.utcnow() + timedelta(minutes=5)
        lock = BeliefLock(TEST_BELIEF_ID, TEST_AUTHOR, expiration=expiration)
        assert not lock.is_expired()
    
    def test_belief_lock_dict_conversion(self):
        """Test converting belief locks to and from dictionaries."""
        lock = BeliefLock(TEST_BELIEF_ID, TEST_AUTHOR, "shared")
        
        # To dictionary
        lock_dict = lock.to_dict()
        assert lock_dict["belief_id"] == TEST_BELIEF_ID
        assert lock_dict["owner"] == TEST_AUTHOR
        assert lock_dict["lock_type"] == "shared"
        assert "acquired_time" in lock_dict
        assert "expiration" in lock_dict
        assert "lock_id" in lock_dict
        
        # From dictionary
        new_lock = BeliefLock.from_dict(lock_dict)
        assert new_lock.belief_id == lock.belief_id
        assert new_lock.owner == lock.owner
        assert new_lock.lock_type == lock.lock_type
        assert new_lock.lock_id == lock.lock_id

class TestBeliefVersionManagerEnhancements:
    """Tests for the enhanced BeliefVersionManager class."""
    
    @pytest.mark.asyncio
    async def test_semantic_versioning(self, belief_version_manager):
        """Test semantic versioning for belief versions."""
        # Track a new version with explicit change type
        result = await belief_version_manager.track_belief_version(
            belief_id=TEST_BELIEF_ID,
            belief_text="This is a test belief with minor addition",
            author=TEST_AUTHOR,
            change_type="minor"
        )
        
        # Check semantic version
        assert "semantic_version" in result
        assert result["semantic_version"]["major"] == 1
        assert result["semantic_version"]["minor"] == 1
        assert result["semantic_version"]["patch"] == 0
        
        # Track another version with a different change type
        result = await belief_version_manager.track_belief_version(
            belief_id=TEST_BELIEF_ID,
            belief_text="This is a completely different belief text",
            author=TEST_AUTHOR,
            change_type="major"
        )
        
        # Check semantic version
        assert "semantic_version" in result
        assert result["semantic_version"]["major"] == 2
        assert result["semantic_version"]["minor"] == 0
        assert result["semantic_version"]["patch"] == 0
    
    @pytest.mark.asyncio
    async def test_conflict_resolution_with_locks(self, belief_version_manager):
        """Test conflict resolution using locks."""
        # Acquire an exclusive lock
        lock_result = await belief_version_manager.acquire_lock(
            belief_id=TEST_BELIEF_ID,
            owner=TEST_AUTHOR
        )
        
        assert lock_result["success"] is True
        assert lock_result["lock_type"] == "exclusive"
        
        # Try to acquire another exclusive lock (should fail)
        second_lock_result = await belief_version_manager.acquire_lock(
            belief_id=TEST_BELIEF_ID,
            owner="another_user"
        )
        
        assert second_lock_result["success"] is False
        
        # Release the lock
        release_result = await belief_version_manager.release_lock(
            belief_id=TEST_BELIEF_ID,
            owner=TEST_AUTHOR
        )
        
        assert release_result["success"] is True
        
        # Now the second user should be able to acquire a lock
        second_lock_result = await belief_version_manager.acquire_lock(
            belief_id=TEST_BELIEF_ID,
            owner="another_user"
        )
        
        assert second_lock_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_shared_locks(self, belief_version_manager):
        """Test shared locks for concurrent read access."""
        # Acquire a shared lock
        lock_result1 = await belief_version_manager.acquire_lock(
            belief_id=TEST_BELIEF_ID,
            owner=TEST_AUTHOR,
            lock_type="shared"
        )
        
        assert lock_result1["success"] is True
        assert lock_result1["lock_type"] == "shared"
        
        # Another user should be able to acquire a shared lock
        lock_result2 = await belief_version_manager.acquire_lock(
            belief_id=TEST_BELIEF_ID,
            owner="another_user",
            lock_type="shared"
        )
        
        assert lock_result2["success"] is True
        assert lock_result2["lock_type"] == "shared"
        
        # But an exclusive lock should fail
        lock_result3 = await belief_version_manager.acquire_lock(
            belief_id=TEST_BELIEF_ID,
            owner="third_user"
        )
        
        assert lock_result3["success"] is False
    
    @pytest.mark.asyncio
    async def test_belief_dependency_tracking(self, belief_version_manager):
        """Test tracking dependencies between beliefs."""
        # Update dependencies
        result = await belief_version_manager.update_dependencies(
            belief_id=TEST_BELIEF_ID,
            depends_on=["belief_abc", "belief_def"]
        )
        
        assert result["success"] is True
        assert "belief_abc" in result["depends_on"]
        assert "belief_def" in result["depends_on"]
        
        # Get dependencies
        deps = await belief_version_manager.get_dependencies(TEST_BELIEF_ID)
        
        assert "depends_on" in deps
        assert "depended_by" in deps
        assert "belief_abc" in deps["depends_on"]
        assert "belief_def" in deps["depends_on"]
    
    @pytest.mark.asyncio
    async def test_change_impact_analysis(self, belief_version_manager):
        """Test analyzing the impact of belief changes."""
        # Set up dependencies for testing
        await belief_version_manager.update_dependencies(
            belief_id=TEST_BELIEF_ID,
            depends_on=["belief_abc"]
        )
        
        # Analyze impact of a change
        impact = await belief_version_manager.analyze_change_impact(
            belief_id=TEST_BELIEF_ID,
            new_belief_text="This is a completely different belief text"
        )
        
        assert impact["success"] is True
        assert "change_type" in impact
        assert "impact_level" in impact
        assert "dependent_count" in impact
        assert "dependent_details" in impact
    
    @pytest.mark.asyncio
    async def test_branching_and_merging(self, belief_version_manager):
        """Test branching and merging belief versions."""
        # Create a branch
        branch_result = await belief_version_manager.create_branch(
            belief_id=TEST_BELIEF_ID,
            branch_name="experimental"
        )
        
        assert branch_result["success"] is True
        assert branch_result["branch"] == "experimental"
        
        # Track a version on the new branch
        version_result = await belief_version_manager.track_belief_version(
            belief_id=TEST_BELIEF_ID,
            belief_text="This is a modified belief on the experimental branch",
            author=TEST_AUTHOR,
            branch="experimental"
        )
        
        assert version_result["branch"] == "experimental"
        
        # Merge the branch back to main
        merge_result = await belief_version_manager.merge_branches(
            belief_id=TEST_BELIEF_ID,
            source_branch="experimental",
            target_branch="main",
            author=TEST_AUTHOR
        )
        
        assert merge_result["success"] is True
        assert merge_result["source_branch"] == "experimental"
        assert merge_result["target_branch"] == "main"
        assert "merge_version" in merge_result
    
    @pytest.mark.asyncio
    async def test_version_comparison(self, belief_version_manager):
        """Test comparing different versions of a belief."""
        # Track a new version
        await belief_version_manager.track_belief_version(
            belief_id=TEST_BELIEF_ID,
            belief_text="This is version 2 of the belief",
            author=TEST_AUTHOR
        )
        
        # Compare versions
        comparison = await belief_version_manager.compare_versions(
            belief_id=TEST_BELIEF_ID,
            version1=1,
            version2=2
        )
        
        assert comparison["success"] is True
        assert comparison["version1"] == 1
        assert comparison["version2"] == 2
        assert "diff" in comparison
        assert "similarity" in comparison
    
    @pytest.mark.asyncio
    async def test_rollback(self, belief_version_manager):
        """Test rolling back to a previous version."""
        # Track a new version
        await belief_version_manager.track_belief_version(
            belief_id=TEST_BELIEF_ID,
            belief_text="This is version 2 of the belief",
            author=TEST_AUTHOR
        )
        
        # Rollback to version 1
        rollback_result = await belief_version_manager.rollback_belief(
            belief_id=TEST_BELIEF_ID,
            version=1,
            author=TEST_AUTHOR
        )
        
        assert rollback_result["success"] is True
        assert rollback_result["original_version"] == 1
        assert "version" in rollback_result
    
    @pytest.mark.asyncio
    async def test_get_belief_version_manager_function(self):
        """Test the get_belief_version_manager function."""
        with patch('app.modules.belief_versioning.BeliefVersionManager') as mock_manager:
            # First call should create a new instance
            manager1 = get_belief_version_manager()
            assert mock_manager.called
            
            # Reset the mock
            mock_manager.reset_mock()
            
            # Second call should return the existing instance
            manager2 = get_belief_version_manager()
            assert not mock_manager.called
            assert manager1 == manager2

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
