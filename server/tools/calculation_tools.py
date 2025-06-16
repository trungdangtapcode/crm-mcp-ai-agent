"""
Calculation tools for MCP server
"""
from typing import Dict, Any

def register_calculation_tools(mcp):
    """Register calculation tools with the MCP server"""
    
    @mcp.tool
    def calculate_expression(expression: str) -> Dict[str, Any]:
        """
        Calculate the result of a mathematical expression
        
        Args:
            expression: The mathematical expression to evaluate
            
        Returns:
            The result of the calculation
        """
        try:
            # Use safer eval with restricted globals
            # Warning: In production, you should use a proper math parser
            import math
            allowed_names = {
                "abs": abs,
                "max": max,
                "min": min,
                "pow": pow,
                "round": round,
                "sum": sum,
                "math": math
            }
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return {
                "expression": expression,
                "result": result,
                "status": "success"
            }
        except Exception as e:
            return {
                "expression": expression,
                "error": str(e),
                "status": "error"
            }
            
    @mcp.tool
    def convert_units(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """
        Convert a value from one unit to another
        
        Args:
            value: The numeric value to convert
            from_unit: The source unit
            to_unit: The target unit
            
        Returns:
            The converted value
        """
        # Define conversion factors
        # This is a simplified version - a real implementation would be more comprehensive
        conversion_factors = {
            # Length
            "m_to_km": 0.001,
            "km_to_m": 1000,
            "m_to_cm": 100,
            "cm_to_m": 0.01,
            "m_to_ft": 3.28084,
            "ft_to_m": 0.3048,
            # Weight/Mass
            "kg_to_g": 1000,
            "g_to_kg": 0.001,
            "kg_to_lb": 2.20462,
            "lb_to_kg": 0.453592,
            # Temperature
            "c_to_f": lambda c: (c * 9/5) + 32,
            "f_to_c": lambda f: (f - 32) * 5/9,
        }
        
        try:
            # Create the conversion key
            key = f"{from_unit.lower()}_to_{to_unit.lower()}"
            
            # Check if conversion is supported
            if key in conversion_factors:
                factor = conversion_factors[key]
                
                # Apply conversion
                if callable(factor):
                    result = factor(value)
                else:
                    result = value * factor
                    
                return {
                    "original_value": value,
                    "original_unit": from_unit,
                    "converted_value": result,
                    "converted_unit": to_unit,
                    "status": "success"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Conversion from {from_unit} to {to_unit} is not supported"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
