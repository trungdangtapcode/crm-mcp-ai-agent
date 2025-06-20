import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartHandler(FileSystemEventHandler):
    def __init__(self):
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