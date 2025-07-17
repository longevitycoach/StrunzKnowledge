"""
Input parser for MCP tools to handle Claude's JSON string inputs

Claude.ai and Claude Desktop sometimes send arrays as JSON strings,
which causes validation errors. This module provides parsing utilities.
"""

import json
from typing import Any, List, Optional, Union


def parse_array_input(value: Union[str, List[Any], None]) -> Optional[List[Any]]:
    """
    Parse input that might be a JSON string array or actual array.
    
    Args:
        value: Either a JSON string like '["item1", "item2"]' or an actual list
        
    Returns:
        Parsed list or None
    """
    if value is None:
        return None
        
    if isinstance(value, list):
        return value
        
    if isinstance(value, str):
        # Check if it looks like a JSON array
        value = value.strip()
        if value.startswith('[') and value.endswith(']'):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
                
        # For invalid JSON that's not an array, return None
        # to avoid wrapping invalid data in a list
            
    return None


def parse_dict_input(value: Union[str, dict, None]) -> Optional[dict]:
    """
    Parse input that might be a JSON string object or actual dict.
    
    Args:
        value: Either a JSON string like '{"key": "value"}' or an actual dict
        
    Returns:
        Parsed dict or None
    """
    if value is None:
        return None
        
    if isinstance(value, dict):
        return value
        
    if isinstance(value, str):
        value = value.strip()
        if value.startswith('{') and value.endswith('}'):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
                
    return None


def preprocess_tool_arguments(tool_name: str, arguments: dict) -> dict:
    """
    Preprocess tool arguments to handle Claude's JSON string inputs.
    
    Args:
        tool_name: Name of the tool being called
        arguments: Raw arguments from Claude
        
    Returns:
        Processed arguments with parsed arrays/dicts
    """
    processed = arguments.copy()
    
    # Handle knowledge_search
    if tool_name == "knowledge_search":
        if "sources" in processed:
            processed["sources"] = parse_array_input(processed["sources"])
        if "filters" in processed:
            processed["filters"] = parse_dict_input(processed["filters"])
        if "user_profile" in processed:
            processed["user_profile"] = parse_dict_input(processed["user_profile"])
            
    # Handle get_trending_insights
    elif tool_name == "get_trending_insights":
        if "categories" in processed:
            processed["categories"] = parse_array_input(processed["categories"])
            
    # Handle other tools with array inputs
    elif tool_name in ["compare_approaches", "analyze_supplement_stack", "nutrition_calculator"]:
        for key in ["alternative_approaches", "criteria", "supplements", "health_goals", 
                    "dietary_preferences", "conditions"]:
            if key in processed:
                processed[key] = parse_array_input(processed[key])
                
    # Handle tools with dict inputs
    elif tool_name in ["find_contradictions", "trace_topic_evolution", "create_health_protocol"]:
        for key in ["time_range", "user_profile"]:
            if key in processed:
                processed[key] = parse_dict_input(processed[key])
                
    return processed