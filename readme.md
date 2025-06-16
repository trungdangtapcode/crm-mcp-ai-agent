
# Agentic AI with Model Context Protocol (MCP)

This project demonstrates how to build an agentic AI system using the Model Context Protocol (MCP). It combines LLMs with tool-calling capabilities to create an interactive agent that can perform various tasks.

## Features

- **Tool Calling**: Dynamically calls appropriate tools based on user requests
- **Conversation Memory**: Maintains context across interactions
- **Multiple Capabilities**: 
  - **Time Tools**: Current time, date information
  - **Weather Tools**: Current weather, forecasts
  - **Search Tools**: Web search, webpage content fetching
  - **Memory Tools**: Store and recall information
  - **Planning Tools**: Task planning and goal achievement
  - **Calculation Tools**: Math calculations, unit conversions
  - **CRM Tools**: Customer information management

## How to Use the System

### User Guide

1. **Start a conversation**: Begin by asking a question or requesting assistance
2. **Use available tools**: You can ask the AI to:
   - **Time Tools**:
     - "What time is it now?"
     - "Tell me today's date and day of the week"
   - **Weather Tools**:
     - "What's the weather like in New York?"
     - "Give me a 5-day forecast for Tokyo"
   - **Search Tools**:
     - "Look up information about quantum computing"
     - "Fetch content from example.com/page"
   - **Memory Tools**:
     - "Remember that my meeting is at 3 PM tomorrow"
     - "What was that meeting time I told you about?"
     - "List everything you remember about me"
   - **Planning Tools**:
     - "Create a plan for launching a website"
     - "Help me plan a trip to Europe"
   - **Calculation Tools**:
     - "Calculate 24 * 7 + 365 / 12"
     - "Convert 10 kilometers to miles"
   - **CRM Tools**:
     - "Create a new customer named John Smith"
     - "What's the contact information for customer ID abc123?"
     - "Update John's email to john@example.com"
     - "List all customers in the database"

3. **Multi-step interactions**: The AI maintains conversation context, so you can refer to previous items in the conversation

4. **Complex workflows**: Combine multiple tools to accomplish more complex tasks:
   ```
   User: What's the weather in London, and can you help me plan a trip there?
   AI: [Uses weather_info to check London weather, then generate_task_plan for trip planning]
   
   User: Create a customer record for Jane Doe with email jane@example.com
   AI: [Uses create_customer to add a new CRM entry]
   User: Now remind me to call Jane next week
   AI: [Uses remember to store this reminder]
   ```

## Architecture

The system consists of the following components:

1. **MCP Server**: Hosts the tools that the AI agent can call
   - **Modular Tool Structure**: Tools are organized in categories
   - **Tool Registry**: Dynamically registers tools with the server
2. **MCP Client**: Interfaces with the MCP server
   - **Dynamic Tool Discovery**: Automatically discovers available tools
   - **Tool Categorization**: Categorizes tools for better organization
3. **Chainlit Web UI**: Provides a chat interface for users
4. **LLM Integration**: Uses models like Mistral AI through API

### Directory Structure

```
app.py                  # Main application entry point
chainlit.md             # Chainlit configuration
config.py               # Configuration and environment variables
handlers.py             # Message handling and tool integration
mcp_client.py           # MCP client implementation
server/                 # Server-side code
├── main.py             # Main server entry point
├── mcp_server.py       # Legacy MCP server (for reference)
├── crm_server.py       # CRM server (for reference)
└── tools/              # Modular tool implementations
    ├── time_tools.py   # Time-related tools
    ├── weather_tools.py # Weather-related tools
    ├── search_tools.py # Search-related tools
    ├── memory_tools.py # Memory-related tools
    ├── planning_tools.py # Planning-related tools
    ├── calculation_tools.py # Calculation-related tools
    └── crm_tools.py    # CRM-related tools
```

## Setup

### Prerequisites

- Python 3.10
- Required Python packages (see requirements.txt)
- Or run conda env
```bash
conda env create -f environment.yml
conda activate mcp-agent
```

### Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following environment variables:
```
API_KEY=your_api_key_here
MCP_SERVER_URL=http://localhost:8000
BASE_URL=https://api.mistral.ai/v1  # or any other LLM API
```

### Running the Application

### Quick Start (Windows)

Use the provided startup script to launch both the MCP server and Chainlit web UI with a single command:

```bash
start.bat
```

### Manual Start

1. Start the MCP server:
```bash
python server/main.py
```

If you want to use HTTP instead:

```bash
fastmcp run server/main.py --transport sse --port 8001
```

2. In a new terminal, start the Chainlit web interface:
```bash
chainlit run app.py
```

3. Open your browser and navigate to `http://localhost:8000` to interact with the agent.

### Docker Deployment

To deploy the full stack using Docker:

```bash
docker-compose up -d
```

This will start:
- MongoDB container for CRM data storage
- MCP Server container with all tools
- Chainlit Web UI container

### Troubleshooting

- **MCP Server not running**: If you get connection errors, make sure the MCP server is running on the correct port
- **Environment variables**: Ensure all environment variables in `.env` are correctly set
- **Package errors**: Verify all required packages are installed with `pip install -r requirements.txt`
- **Port conflicts**: If port 8000 is already in use, modify the port in `mcp_server.py` and update `MCP_SERVER_URL` accordingly

## Extending the System

### Adding New Tools

The MCP server has been restructured into a modular architecture for better organization. To add a new tool:

1. **Choose the appropriate module** in the `server/tools/` directory or create a new one
2. **Add your tool function** to the module:

```python
# In server/tools/your_category_tools.py
def register_your_category_tools(mcp):
    @mcp.tool
    def your_tool_function(param1: str, param2: int) -> Dict[str, Any]:
        """
        Description of what your tool does
        
        Args:
            param1: Description of param1
            param2: Description of param2
            
        Returns:
            Description of the return value
        """
        # Tool implementation
        result = {}
        # Do something with params
        return result
```

3. **Import and register your module** in `server/main.py`:

```python
# Import your module
from tools.your_category_tools import register_your_category_tools

# In create_mcp_server function, add:
logger.info("Registering your category tools...")
register_your_category_tools(mcp)
```

### Complete Tool Development Workflow

1. **Define the tool function** in `mcp_server.py`:
   - Use type hints for parameters and return values
   - Write a clear docstring explaining what the tool does
   - Implement the tool logic

2. **Restart the MCP server** to register the new tool:
   ```bash
   # Stop the current server (Ctrl+C) and restart
   python mcp_server.py
   ```

3. **Test the tool** by asking the AI to use it in a conversation

### Customizing the UI

To modify the Chainlit UI appearance:

1. Edit `chainlit.md` to change the welcome message and other UI elements
2. Modify CSS styles in a `.css` file within a `pages` directory 
3. Update the greeting message in `app.py` by changing the content in the `start()` function

## Advanced Usage and Modification

### System Architecture Diagram

```
┌────────────────┐     ┌─────────────────┐     ┌──────────────┐
│                │     │                 │     │              │
│  Chainlit UI   │◄───►│  Handlers.py    │◄───►│  LLM API     │
│  (app.py)      │     │                 │     │              │
│                │     │                 │     │              │
└────────────────┘     └────────┬────────┘     └──────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │                 │
                       │  MCP Client     │
                       │  (mcp_client.py)│
                       │                 │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │                 │
                       │  MCP Server     │
                       │  (mcp_server.py)│
                       │                 │
                       └─────────────────┘
```

### Key Files and Their Roles

- **app.py**: Main application entry point for Chainlit
- **handlers.py**: Manages message processing and tool calling workflow  
- **mcp_client.py**: Client interface to the MCP server
- **config.py**: Configuration and environment variables
- **requirements.txt**: Required Python packages
- **server/**:
  - **main.py**: Modular MCP server entry point
  - **tools/**: Directory containing categorized tool implementations
    - **time_tools.py**: Time and date related tools
    - **weather_tools.py**: Weather information tools
    - **search_tools.py**: Web search and content fetching tools
    - **memory_tools.py**: Memory storage and recall tools
    - **planning_tools.py**: Task planning tools
    - **calculation_tools.py**: Math calculation tools
    - **crm_tools.py**: CRM integration with MongoDB support
- **Dockerfile.server**: Docker configuration for MCP server
- **Dockerfile.client**: Docker configuration for Chainlit web UI
- **docker-compose.yml**: Docker Compose configuration for full stack deployment

### Modifying the System

#### Adding New LLM Providers

To use a different LLM provider:

1. Update the `BASE_URL` in `.env` to point to your LLM provider's API endpoint
2. Modify `handlers.py` to adapt the request format if necessary  

#### Enhancing the Memory System

To implement persistent memory:

1. Add database connection code to `mcp_server.py`
2. Modify the `remember` and `recall` functions to use the database
3. Add initialization code to set up the database connection

## Testing and Benchmarking

The project includes testing and benchmarking tools:

```bash
# Run tool tests
python server/test_mcp.py

# Run performance benchmarks
python server/benchmark.py
```

## MongoDB Integration for CRM Tools

The CRM tools use MongoDB for persistent storage:

1. Configure MongoDB connection in your `.env` file:
```
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=crm
MONGO_COLLECTION=customers
```

2. If MongoDB is not available, the system will automatically fall back to in-memory storage.

## Production Considerations

For a production deployment, consider:

- **Database**: MongoDB integration is already included for CRM tools
- **Containerization**: Docker and Docker Compose files are provided
- **Security**:
  - Implement authentication for the MCP server
  - Set up proper API key management
  - Add rate limiting and request validation
- **Monitoring**:
  - Set up logging aggregation (ELK, Grafana, etc.)
  - Implement health checks and monitoring
- **Scaling**:
  - Consider using Kubernetes for container orchestration
  - Implement load balancing for high availability
- **Testing**:
  - Add more unit and integration tests
  - Set up CI/CD pipelines
- **Web Interface**:
  - Set up a proper reverse proxy (Nginx, Traefik)
  - Implement HTTPS with SSL/TLS certificates

## License

[MIT License](LICENSE)
