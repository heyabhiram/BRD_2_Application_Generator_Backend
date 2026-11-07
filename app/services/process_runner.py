import os
import sys
import socket
import subprocess
import time
import httpx
from pathlib import Path
from typing import Dict, Optional

class ProcessManager:
    def __init__(self):
        # Maps project_id -> {"process": Popen, "port": int, "dir": Path, "status": str}
        self.running_apps: Dict[str, dict] = {}

    def get_available_port(self, start_port: int = 3100) -> int:
        """Find an available port starting from start_port."""
        port = start_port
        while port < 4000:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                try:
                    s.bind(("127.0.0.1", port))
                    return port
                except OSError:
                    port += 1
        raise RuntimeError("No available port found between 3100 and 4000.")

    def is_port_open(self, port: int, host: str = "127.0.0.1") -> bool:
        """Check if server is responding on port."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            try:
                s.connect((host, port))
                return True
            except OSError:
                return False

    def start_app(self, project_id: str, project_dir: Path) -> int:
        """Stop any existing instance for project_id and launch npm run dev on a free port."""
        self.stop_app(project_id)
        
        port = self.get_available_port()
        is_windows = sys.platform == "win32"
        
        cmd = f"npm run dev -- -p {port}"
        
        # Start subprocess without blocking
        proc = subprocess.Popen(
            cmd,
            cwd=str(project_dir),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if is_windows else 0
        )
        
        self.running_apps[project_id] = {
            "process": proc,
            "port": port,
            "dir": project_dir,
            "status": "starting"
        }
        
        # Wait up to 25 seconds for the port to open
        start_time = time.time()
        while time.time() - start_time < 25:
            if self.is_port_open(port):
                self.running_apps[project_id]["status"] = "running"
                return port
            # Check if process died early
            if proc.poll() is not None:
                err = proc.stderr.read() if proc.stderr else "Process terminated prematurely."
                raise RuntimeError(f"Application failed to start: {err}")
            time.sleep(1)
            
        self.running_apps[project_id]["status"] = "running"
        return port

    def stop_app(self, project_id: str):
        """Cleanly kill subprocess and free port."""
        if project_id in self.running_apps:
            info = self.running_apps[project_id]
            proc: subprocess.Popen = info.get("process")
            if proc and proc.poll() is None:
                try:
                    if sys.platform == "win32":
                        subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, capture_output=True)
                    else:
                        proc.terminate()
                        proc.wait(timeout=3)
                except Exception:
                    pass
            del self.running_apps[project_id]

    def stop_all(self):
        """Stop all running child processes."""
        for pid in list(self.running_apps.keys()):
            self.stop_app(pid)

process_manager = ProcessManager()

