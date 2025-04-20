from datetime import datetime

class ReflectionAnalyzer:
    """
    Analyzes reflection quality and detects issues in the reflection process.
    """
    
    def __init__(self, memory):
        self.memory = memory
        
    def analyze_reflection(self):
        """
        Analyzes the last reflection in memory and returns any issues found.
        """
        reflection = self.memory.get("last_reflection", {})
        issues = {}
        
        # Check reflection confidence
        confidence = reflection.get("confidence", 1.0)
        if confidence < 0.5:
            issues["low_confidence"] = {
                "value": confidence,
                "threshold": 0.5,
                "description": "Reflection confidence is below acceptable threshold"
            }
        
        # Check reflection completeness
        if not reflection.get("summary") or len(reflection.get("summary", "")) < 10:
            issues["incomplete_reflection"] = {
                "description": "Reflection summary is missing or too short"
            }
        
        # Check for skipped agents
        completed_steps = self.memory.get("completed_steps", [])
        planned_steps = self.memory.get("planned_steps", [])
        
        if planned_steps and len(completed_steps) < len(planned_steps):
            skipped_steps = [step for step in planned_steps if step not in completed_steps]
            if skipped_steps:
                issues["skipped_steps"] = {
                    "skipped": skipped_steps,
                    "description": f"Some planned steps were skipped: {', '.join(skipped_steps)}"
                }
        
        # Check for repeated reflections (sign of being stuck)
        reflections_history = self.memory.get("reflections_history", [])
        if len(reflections_history) >= 3:
            last_three = reflections_history[-3:]
            summaries = [r.get("summary", "") for r in last_three]
            
            # Check if the last three summaries are very similar
            if len(set(summaries)) == 1 and summaries[0]:  # All identical and not empty
                issues["repetitive_reflections"] = {
                    "description": "Last three reflections are identical, system may be stuck"
                }
        
        return issues if issues else None
