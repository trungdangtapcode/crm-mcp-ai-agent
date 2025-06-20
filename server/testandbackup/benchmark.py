"""
Benchmarking script for MCP server
This script performs a series of benchmarks to measure the performance of the MCP server.
"""

import asyncio
import time
import logging
import statistics
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_client import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("benchmark_mcp")

MCP_SERVER_URL = "http://localhost"
ITERATIONS = 10

async def measure_tool_performance(client: MCPClient, tool_name: str, params: Dict[str, Any], iterations: int = 5) -> Dict[str, Any]:
    """Measure the performance of a specific tool"""
    
    execution_times = []
    results = []
    
    for i in range(iterations):
        start_time = time.time()
        result = await client.call_tool(tool_name, **params)
        end_time = time.time()
        
        execution_time = end_time - start_time
        execution_times.append(execution_time)
        results.append(result)
    
    # Calculate statistics
    avg_time = statistics.mean(execution_times)
    median_time = statistics.median(execution_times)
    min_time = min(execution_times)
    max_time = max(execution_times)
    
    return {
        "tool": tool_name,
        "params": params,
        "stats": {
            "iterations": iterations,
            "avg_time_ms": round(avg_time * 1000, 2),
            "median_time_ms": round(median_time * 1000, 2),
            "min_time_ms": round(min_time * 1000, 2),
            "max_time_ms": round(max_time * 1000, 2)
        },
        "sample_result": results[0]
    }

async def run_benchmarks():
    """Run benchmarks on the MCP server"""
    
    logger.info(f"Connecting to MCP server at {MCP_SERVER_URL}")
    
    # Initialize client
    client = MCPClient(MCP_SERVER_URL)
    await client.initialize()
    
    # Define benchmarks
    benchmarks = [
        {
            "name": "Simple time query",
            "tool": "get_current_time",
            "params": {}
        },
        {
            "name": "Weather lookup",
            "tool": "weather_info",
            "params": {"location": "New York"}
        },
        {
            "name": "Web search",
            "tool": "search_web",
            "params": {"query": "MCP protocol"}
        },
        {
            "name": "Memory store and recall",
            "tool": "remember",
            "params": {"key": "benchmark", "value": "test value"}
        },
        {
            "name": "Task planning",
            "tool": "generate_task_plan",
            "params": {"goal": "Implement a benchmark system"}
        },
        {
            "name": "Math calculation",
            "tool": "calculate_expression",
            "params": {"expression": "math.sqrt(25) + pow(2, 8)"}
        }
    ]
    
    # Run benchmarks
    logger.info(f"Running benchmarks with {ITERATIONS} iterations each")
    
    results = []
    for benchmark in benchmarks:
        logger.info(f"Benchmarking: {benchmark['name']}")
        result = await measure_tool_performance(
            client, 
            benchmark["tool"], 
            benchmark["params"], 
            ITERATIONS
        )
        results.append({
            "name": benchmark["name"],
            **result
        })
    
    # Print results
    logger.info("\nBenchmark Results:")
    logger.info("=" * 80)
    logger.info(f"{'Tool Name':<25} {'Avg (ms)':<12} {'Median (ms)':<12} {'Min (ms)':<12} {'Max (ms)':<12}")
    logger.info("-" * 80)
    
    for result in results:
        stats = result["stats"]
        logger.info(
            f"{result['name']:<25} "
            f"{stats['avg_time_ms']:<12.2f} "
            f"{stats['median_time_ms']:<12.2f} "
            f"{stats['min_time_ms']:<12.2f} "
            f"{stats['max_time_ms']:<12.2f}"
        )
    
    logger.info("=" * 80)
    
    # Calculate overall stats
    all_avg_times = [r["stats"]["avg_time_ms"] for r in results]
    overall_avg = statistics.mean(all_avg_times)
    logger.info(f"Overall average response time: {overall_avg:.2f} ms")

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
