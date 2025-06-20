import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def kill_port_windows(port: int):
    # Find all PIDs using the port
    result = subprocess.run(
        f'netstat -ano | findstr :{port}',
        shell=True,
        capture_output=True,
        text=True
    )

    # Extract unique PIDs from the result
    pids = set()
    for line in result.stdout.strip().split('\n'):
        if line:
            try:
                parts = line.strip().split()
                pid = parts[-1]
                if pid.isdigit():
                    pids.add(pid)
            except IndexError:
                continue

    # Kill each PID
    for pid in pids:
        subprocess.run(f'taskkill /PID {pid} /F', shell=True)

    cmd = r'''for /f "tokens=5" %a in ('netstat -aon ^| findstr :8001') do taskkill /PID %a /F'''
    result = subprocess.run(cmd, shell=True)
    print(f"Killed processes on port {port}: {result.stderr}")

class RestartHandler(FileSystemEventHandler):
    def __init__(self):
        kill_port_windows(8001)    
        self.process = None
        self.start_server()

    def start_server(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        print("Starting FastMCP server...")
        self.process = subprocess.Popen(
            ["uv", "run", "fastmcp", "run", "main.py:mcp", "--transport", "sse", "--port", "8001", "--host", "0.0.0.0"]
        )

    def on_any_event(self, event):
        if event.is_directory or event.src_path.endswith(".py"):
            print(f"Detected change in {event.src_path}, restarting server...")
            # Kill process port 8001 if it's running
            if self.process:
                self.process.terminate()
                self.process.wait()
            # Kill all process with port 8001
            kill_port_windows(8001)            
            self.start_server()

if __name__ == "__main__":
    event_handler = RestartHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        event_handler.process.terminate()
    observer.join()