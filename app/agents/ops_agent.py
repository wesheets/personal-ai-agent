from app.agents.memory_agent import handle_memory_task

def handle_ops_task(task_input):
    """
    Process operations tasks, including vertical scaffolding.
    
    Args:
        task_input: The input task string
        
    Returns:
        A string response based on the task execution
    """
    # Handle LifeTree vertical scaffolding
    if "LifeTree" in task_input:
        # Log the operation to memory
        handle_memory_task("LOG: OpsAgent created LifeTree vertical on request from Core.Forge")
        
        # Return success message with details
        return "Scaffolded LifeTree vertical agent structure with basic memory logging and journaling features."
    
    # Handle other operations tasks
    return f"OpsAgent: Executing system-level operation for '{task_input}'."
