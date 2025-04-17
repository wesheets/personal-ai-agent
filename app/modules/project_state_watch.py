"""
Project State Watch Module

This module provides functionality for watching project state changes,
allowing agents or orchestrator to listen or poll for changes.
"""
import logging
import json
import os
import time
import threading
from typing import Dict, Any, List, Optional, Callable

# Configure logging
logger = logging.getLogger("app.modules.project_state_watch")

# Import project_state for tracking project status
try:
    from app.modules.project_state import read_project_state
    PROJECT_STATE_AVAILABLE = True
except ImportError:
    PROJECT_STATE_AVAILABLE = False
    print("❌ project_state import failed")

# Import agent_retry for retry and recovery flow
try:
    from app.modules.agent_retry import check_for_unblocked_agents
    AGENT_RETRY_AVAILABLE = True
except ImportError:
    AGENT_RETRY_AVAILABLE = False
    print("❌ agent_retry import failed")

class ProjectStateWatcher:
    """
    Watches for changes in project state and triggers callbacks when changes occur.
    """
    def __init__(self):
        self.watchers = {}
        self.polling_threads = {}
        self.subscribers = {}
        self.last_state = {}
        self.running = True
    
    def start_watching(self, project_id: str, callback: Callable[[Dict[str, Any], Dict[str, Any]], None], 
                      interval: int = 30) -> Dict[str, Any]:
        """
        Start watching for changes in project state.
        
        Args:
            project_id: The project identifier
            callback: Function to call when state changes, receives (old_state, new_state)
            interval: Polling interval in seconds
            
        Returns:
            Dict containing the result of the operation
        """
        try:
            if not PROJECT_STATE_AVAILABLE:
                error_msg = "Project state not available, cannot watch for changes"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id
                }
            
            # Create watcher entry
            watcher_id = f"{project_id}_{int(time.time())}"
            
            if project_id not in self.watchers:
                self.watchers[project_id] = {}
                
                # Initialize last state
                self.last_state[project_id] = read_project_state(project_id)
                
                # Start polling thread if not already running
                if project_id not in self.polling_threads or not self.polling_threads[project_id].is_alive():
                    self._start_polling_thread(project_id, interval)
            
            # Register callback
            self.watchers[project_id][watcher_id] = callback
            
            logger.info(f"Started watching project state for {project_id} with interval {interval}s")
            print(f"👀 Started watching project state for {project_id} with interval {interval}s")
            
            return {
                "status": "success",
                "message": f"Started watching project state for {project_id}",
                "project_id": project_id,
                "watcher_id": watcher_id,
                "interval": interval
            }
            
        except Exception as e:
            error_msg = f"Error starting project state watch for {project_id}: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "error": str(e)
            }
    
    def stop_watching(self, project_id: str, watcher_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Stop watching for changes in project state.
        
        Args:
            project_id: The project identifier
            watcher_id: Optional watcher identifier to stop specific watcher
            
        Returns:
            Dict containing the result of the operation
        """
        try:
            if project_id not in self.watchers:
                return {
                    "status": "success",
                    "message": f"No watchers found for project {project_id}",
                    "project_id": project_id
                }
            
            # Stop specific watcher if watcher_id is provided
            if watcher_id:
                if watcher_id in self.watchers[project_id]:
                    del self.watchers[project_id][watcher_id]
                    logger.info(f"Stopped watcher {watcher_id} for project {project_id}")
                    print(f"👋 Stopped watcher {watcher_id} for project {project_id}")
                else:
                    return {
                        "status": "error",
                        "message": f"Watcher {watcher_id} not found for project {project_id}",
                        "project_id": project_id
                    }
            else:
                # Stop all watchers for project
                self.watchers[project_id] = {}
                logger.info(f"Stopped all watchers for project {project_id}")
                print(f"👋 Stopped all watchers for project {project_id}")
            
            # Stop polling thread if no more watchers and subscribers
            if (not self.watchers[project_id] and 
                (project_id not in self.subscribers or not self.subscribers[project_id])):
                self.running = False
                if project_id in self.polling_threads and self.polling_threads[project_id].is_alive():
                    self.polling_threads[project_id].join(1)  # Wait for thread to terminate
                    del self.polling_threads[project_id]
            
            return {
                "status": "success",
                "message": f"Stopped {'watcher ' + watcher_id if watcher_id else 'all watchers'} for project {project_id}",
                "project_id": project_id
            }
            
        except Exception as e:
            error_msg = f"Error stopping project state watch for {project_id}: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "error": str(e)
            }
    
    def subscribe(self, project_id: str, subscriber_id: str) -> Dict[str, Any]:
        """
        Subscribe to project state changes.
        
        Args:
            project_id: The project identifier
            subscriber_id: Subscriber identifier
            
        Returns:
            Dict containing the result of the operation
        """
        try:
            if not PROJECT_STATE_AVAILABLE:
                error_msg = "Project state not available, cannot subscribe to changes"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id
                }
            
            # Create subscriber entry
            if project_id not in self.subscribers:
                self.subscribers[project_id] = set()
                
                # Initialize last state
                self.last_state[project_id] = read_project_state(project_id)
                
                # Start polling thread if not already running
                if project_id not in self.polling_threads or not self.polling_threads[project_id].is_alive():
                    self._start_polling_thread(project_id)
            
            # Add subscriber
            self.subscribers[project_id].add(subscriber_id)
            
            logger.info(f"Subscriber {subscriber_id} subscribed to project state changes for {project_id}")
            print(f"🔔 Subscriber {subscriber_id} subscribed to project state changes for {project_id}")
            
            return {
                "status": "success",
                "message": f"Subscribed to project state changes for {project_id}",
                "project_id": project_id,
                "subscriber_id": subscriber_id,
                "current_state": self.last_state[project_id]
            }
            
        except Exception as e:
            error_msg = f"Error subscribing to project state changes for {project_id}: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "error": str(e)
            }
    
    def unsubscribe(self, project_id: str, subscriber_id: str) -> Dict[str, Any]:
        """
        Unsubscribe from project state changes.
        
        Args:
            project_id: The project identifier
            subscriber_id: Subscriber identifier
            
        Returns:
            Dict containing the result of the operation
        """
        try:
            if project_id not in self.subscribers:
                return {
                    "status": "success",
                    "message": f"No subscribers found for project {project_id}",
                    "project_id": project_id
                }
            
            # Remove subscriber
            if subscriber_id in self.subscribers[project_id]:
                self.subscribers[project_id].remove(subscriber_id)
                logger.info(f"Subscriber {subscriber_id} unsubscribed from project state changes for {project_id}")
                print(f"👋 Subscriber {subscriber_id} unsubscribed from project state changes for {project_id}")
            else:
                return {
                    "status": "error",
                    "message": f"Subscriber {subscriber_id} not found for project {project_id}",
                    "project_id": project_id
                }
            
            # Stop polling thread if no more subscribers and watchers
            if (not self.subscribers[project_id] and 
                (project_id not in self.watchers or not self.watchers[project_id])):
                self.running = False
                if project_id in self.polling_threads and self.polling_threads[project_id].is_alive():
                    self.polling_threads[project_id].join(1)  # Wait for thread to terminate
                    del self.polling_threads[project_id]
            
            return {
                "status": "success",
                "message": f"Unsubscribed from project state changes for {project_id}",
                "project_id": project_id,
                "subscriber_id": subscriber_id
            }
            
        except Exception as e:
            error_msg = f"Error unsubscribing from project state changes for {project_id}: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "error": str(e)
            }
    
    def get_subscribers(self, project_id: str) -> Dict[str, Any]:
        """
        Get subscribers for a project.
        
        Args:
            project_id: The project identifier
            
        Returns:
            Dict containing the subscribers
        """
        try:
            if project_id not in self.subscribers:
                return {
                    "status": "success",
                    "message": f"No subscribers found for project {project_id}",
                    "project_id": project_id,
                    "subscribers": []
                }
            
            return {
                "status": "success",
                "message": f"Subscribers for project {project_id}",
                "project_id": project_id,
                "subscribers": list(self.subscribers[project_id])
            }
            
        except Exception as e:
            error_msg = f"Error getting subscribers for project {project_id}: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "error": str(e)
            }
    
    def get_current_state(self, project_id: str) -> Dict[str, Any]:
        """
        Get current project state.
        
        Args:
            project_id: The project identifier
            
        Returns:
            Dict containing the current state
        """
        try:
            if not PROJECT_STATE_AVAILABLE:
                error_msg = "Project state not available, cannot get current state"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id
                }
            
            # Read current state
            current_state = read_project_state(project_id)
            
            return {
                "status": "success",
                "message": f"Current state for project {project_id}",
                "project_id": project_id,
                "state": current_state
            }
            
        except Exception as e:
            error_msg = f"Error getting current state for project {project_id}: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "error": str(e)
            }
    
    def _start_polling_thread(self, project_id: str, interval: int = 30) -> None:
        """
        Start polling thread for project state changes.
        
        Args:
            project_id: The project identifier
            interval: Polling interval in seconds
        """
        def poll_project_state():
            while self.running:
                try:
                    # Read current state
                    current_state = read_project_state(project_id)
                    
                    # Check if state has changed
                    if project_id in self.last_state and current_state != self.last_state[project_id]:
                        old_state = self.last_state[project_id]
                        
                        # Notify watchers
                        if project_id in self.watchers:
                            for watcher_id, callback in self.watchers[project_id].items():
                                try:
                                    callback(old_state, current_state)
                                except Exception as e:
                                    logger.error(f"Error in watcher callback {watcher_id}: {str(e)}")
                        
                        # Check for unblocked agents
                        if AGENT_RETRY_AVAILABLE:
                            unblocked_agents = check_for_unblocked_agents(project_id)
                            if unblocked_agents:
                                logger.info(f"Unblocked agents for project {project_id}: {unblocked_agents}")
                                print(f"🔓 Unblocked agents for project {project_id}: {[a['agent_id'] for a in unblocked_agents]}")
                        
                        # Update last state
                        self.last_state[project_id] = current_state
                        
                        logger.info(f"Project state changed for {project_id}")
                        print(f"📊 Project state changed for {project_id}")
                    
                    # Sleep for interval
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Error in polling thread for project {project_id}: {str(e)}")
                    time.sleep(interval)  # Sleep even on error to avoid tight loop
        
        # Start polling thread
        thread = threading.Thread(target=poll_project_state, daemon=True)
        thread.start()
        self.polling_threads[project_id] = thread
        
        logger.info(f"Started polling thread for project {project_id} with interval {interval}s")
        print(f"🔄 Started polling thread for project {project_id} with interval {interval}s")

# Create a singleton instance
state_watcher = ProjectStateWatcher()

def start_watching(project_id: str, callback: Callable[[Dict[str, Any], Dict[str, Any]], None], 
                  interval: int = 30) -> Dict[str, Any]:
    """
    Start watching for changes in project state.
    
    Args:
        project_id: The project identifier
        callback: Function to call when state changes, receives (old_state, new_state)
        interval: Polling interval in seconds
        
    Returns:
        Dict containing the result of the operation
    """
    return state_watcher.start_watching(project_id, callback, interval)

def stop_watching(project_id: str, watcher_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Stop watching for changes in project state.
    
    Args:
        project_id: The project identifier
        watcher_id: Optional watcher identifier to stop specific watcher
        
    Returns:
        Dict containing the result of the operation
    """
    return state_watcher.stop_watching(project_id, watcher_id)

def subscribe(project_id: str, subscriber_id: str) -> Dict[str, Any]:
    """
    Subscribe to project state changes.
    
    Args:
        project_id: The project identifier
        subscriber_id: Subscriber identifier
        
    Returns:
        Dict containing the result of the operation
    """
    return state_watcher.subscribe(project_id, subscriber_id)

def unsubscribe(project_id: str, subscriber_id: str) -> Dict[str, Any]:
    """
    Unsubscribe from project state changes.
    
    Args:
        project_id: The project identifier
        subscriber_id: Subscriber identifier
        
    Returns:
        Dict containing the result of the operation
    """
    return state_watcher.unsubscribe(project_id, subscriber_id)

def get_subscribers(project_id: str) -> Dict[str, Any]:
    """
    Get subscribers for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing the subscribers
    """
    return state_watcher.get_subscribers(project_id)

def get_current_state(project_id: str) -> Dict[str, Any]:
    """
    Get current project state.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing the current state
    """
    return state_watcher.get_current_state(project_id)
