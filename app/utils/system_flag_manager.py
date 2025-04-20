class SystemFlagManager:
    """
    Manages system flags for critical issues detected by the CTO agent.
    """
    
    def __init__(self, project_memory, project_id):
        self.project_memory = project_memory
        self.project_id = project_id
        
    def set_system_flag(self, level, origin, issues):
        """
        Sets a system flag in the project memory.
        
        Args:
            level (str): Flag level - 'info', 'warning', or 'error'
            origin (str): Component that originated the flag
            issues (dict): Dictionary of issues that triggered the flag
        """
        from datetime import datetime
        
        # Initialize system_flags array if it doesn't exist
        if "system_flags" not in self.project_memory.get(self.project_id, {}):
            self.project_memory[self.project_id]["system_flags"] = []
        
        # Create the flag
        flag = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "origin": origin,
            "issues": issues
        }
        
        # Add the flag to the system_flags array
        self.project_memory[self.project_id]["system_flags"].append(flag)
        
        return flag
    
    def get_active_flags(self, level=None):
        """
        Gets all active system flags, optionally filtered by level.
        
        Args:
            level (str, optional): Filter flags by level ('info', 'warning', 'error')
            
        Returns:
            list: List of active system flags
        """
        flags = self.project_memory.get(self.project_id, {}).get("system_flags", [])
        
        if level:
            return [flag for flag in flags if flag.get("level") == level]
        
        return flags
    
    def clear_flags(self, origin=None):
        """
        Clears all system flags, optionally filtered by origin.
        
        Args:
            origin (str, optional): Clear only flags from this origin
        """
        if origin:
            self.project_memory[self.project_id]["system_flags"] = [
                flag for flag in self.project_memory.get(self.project_id, {}).get("system_flags", [])
                if flag.get("origin") != origin
            ]
        else:
            self.project_memory[self.project_id]["system_flags"] = []
