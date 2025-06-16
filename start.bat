@echo off
REM Start script for Agentic AI with MCP
REM This script starts both the MCP server and the Chainlit web UI

echo Starting Agentic AI with MCP...
echo.

REM Set virtual environment (if using conda or venv, uncomment the appropriate line)
REM call activate mcp-agent
REM call venv\Scripts\activate.bat

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not available. Please install Python and try again.
    exit /b 1
)

echo Checking dependencies...
pip list | findstr "fastmcp chainlit openai httpx pydantic" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting MCP Server...
start cmd /k "python server/main.py"

echo Waiting for server to initialize...
timeout /t 5 /nobreak >nul

echo Starting Chainlit Web UI...
start cmd /k "chainlit run app.py"

echo.
echo Agentic AI with MCP is starting...
echo Server: http://localhost:8000
echo Web UI: http://localhost:8000
echo.
echo Press any key to open the web interface in your browser...
pause >nul

start http://localhost:8000
