"""
HAL Code Generator Module

This module provides functions for HAL agent to generate code based on build tasks.
It integrates with the memory system and code generation modules.
"""

import logging
import traceback
from typing import Dict, Any, Optional
import datetime
import json

# Import code generation modules
from app.modules.code_generation.react_generator import generate_code_from_instruction

# Import memory operations
from app.api.modules.memory import read_memory, write_memory

# Configure logging
logger = logging.getLogger("modules.code_generation.hal_code_generator")

async def process_build_task(loop_id: str, input_key: str, target_file: str) -> Dict[str, Any]:
    """
    Process a build task from memory and generate code.
    
    Args:
        loop_id: The loop identifier
        input_key: The memory key to read input from
        target_file: The target file for the generated code
        
    Returns:
        Dict containing the result of the operation
    """
    try:
        logger.info(f"Processing build task for loop: {loop_id}, input_key: {input_key}")
        print(f"🔄 Processing build task for loop: {loop_id}, input_key: {input_key}")
        
        # Read the build task from memory
        memory_data = await read_memory(
            agent_id=loop_id,
            memory_type="loop",
            tag=input_key
        )
        
        if not memory_data:
            error_msg = f"Memory not found for key: {input_key} in loop: {loop_id}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "loop_id": loop_id,
                "input_key": input_key,
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Extract the instruction from memory
        instruction = memory_data.get("content", "")
        if not instruction:
            error_msg = f"No content found in memory for key: {input_key}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "loop_id": loop_id,
                "input_key": input_key,
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Generate code based on the instruction
        code_result = generate_code_from_instruction(instruction, target_file)
        
        if code_result.get("status") != "success":
            error_msg = f"Failed to generate code: {code_result.get('message', 'Unknown error')}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "loop_id": loop_id,
                "input_key": input_key,
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Prepare the response data
        generated_code = code_result.get("code", "")
        timestamp = datetime.datetime.now().isoformat()
        
        response_data = {
            "code": generated_code,
            "target_file": target_file,
            "timestamp": timestamp,
            "component_type": code_result.get("component_type", "generic"),
            "features": code_result.get("features", [])
        }
        
        # Write the generated code to memory
        output_key = f"hal_{input_key}_response"
        
        memory_write_result = await write_memory(
            agent_id=loop_id,
            memory_type="loop",
            tag=output_key,
            value=response_data
        )
        
        if not memory_write_result or memory_write_result.get("status") != "ok":
            error_msg = f"Failed to write generated code to memory: {memory_write_result.get('message', 'Unknown error')}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "loop_id": loop_id,
                "input_key": input_key,
                "output_key": output_key,
                "timestamp": timestamp
            }
        
        logger.info(f"Successfully processed build task for loop: {loop_id}, input_key: {input_key}")
        print(f"✅ Successfully processed build task for loop: {loop_id}, input_key: {input_key}")
        print(f"📄 Generated code for: {target_file}")
        print(f"🧠 Written to memory key: {output_key}")
        
        return {
            "status": "success",
            "loop_id": loop_id,
            "input_key": input_key,
            "output_key": output_key,
            "target_file": target_file,
            "timestamp": timestamp,
            "message": f"Successfully generated code for {target_file}"
        }
        
    except Exception as e:
        error_msg = f"Error processing build task: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg,
            "loop_id": loop_id,
            "input_key": input_key,
            "timestamp": datetime.datetime.now().isoformat()
        }
