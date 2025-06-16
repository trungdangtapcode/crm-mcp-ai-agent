# MCP Server Tools

This directory contains the modular tool implementations for the MCP server. Each file represents a category of tools and follows a consistent pattern to register tools with the MCP server.

## Directory Structure

- `__init__.py`: Makes the directory a proper Python package
- `time_tools.py`: Time and date related tools
- `weather_tools.py`: Weather information tools
- `search_tools.py`: Web search and content fetching tools
- `memory_tools.py`: Information storage and recall tools  
- `planning_tools.py`: Task and goal planning tools
- `calculation_tools.py`: Math calculation and unit conversion tools
- `crm_tools.py`: Customer relationship management tools

## How to Add New Tools

### 1. Add to an Existing Category

To add a new tool to an existing category, locate the appropriate file and add your tool function:

```python
# In the appropriate file, e.g., weather_tools.py
def register_weather_tools(mcp):
    # ...existing tools...

    @mcp.tool
    def your_new_tool(param1: str) -> Dict[str, Any]:
        """
        Description of your new tool
        
        Args:
            param1: Description of parameter
            
        Returns:
            Description of return value
        """
        # Implementation
        return {"result": "value"}
```

### 2. Create a New Category

To create a new category of tools:

1. Create a new file in this directory named `<category>_tools.py`
2. Implement the tool registration function:

```python
"""
Description of your tool category
"""
from typing import Dict, Any, List, Optional

def register_your_category_tools(mcp):
    """Register your category tools with the MCP server"""
    
    @mcp.tool
    def your_tool(param1: str) -> Dict[str, Any]:
        """
        Description of your tool
        
        Args:
            param1: Description of parameter
            
        Returns:
            Description of return value
        """
        # Implementation
        return {"result": "value"}
```

3. Import and register your category in `server/main.py`:

```python
from tools.your_category_tools import register_your_category_tools

# In create_mcp_server function:
logger.info("Registering your category tools...")
register_your_category_tools(mcp)
```

## Best Practices

1. **Type hints**: Always use proper type hints for parameters and return values
2. **Docstrings**: Include clear docstrings with descriptions of parameters and return values
3. **Error handling**: Implement proper error handling and return meaningful error messages
4. **Consistency**: Follow the same pattern as existing tools for consistency
5. **Modularity**: Keep tools organized by category and purpose
