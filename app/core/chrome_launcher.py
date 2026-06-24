import socket
import subprocess
import time
from pathlib import Path


class ChromeLauncher:
    @staticmethod
    def is_port_open(port: int, timeout: float = 0.2) -> bool:
        if port <= 0:
            return False

        try:
            with socket.create_connection(("127.0.0.1", port), timeout=timeout):
                return True
        except OSError:
            return False

    @staticmethod
    def wait_until_ready(port: int, timeout_seconds: float = 10.0) -> bool:
        deadline = time.time() + timeout_seconds

        while time.time() < deadline:
            if ChromeLauncher.is_port_open(port, timeout=0.25):
                return True
            time.sleep(0.25)

        return False

    @staticmethod
    def launch(profile: dict):
        chrome_path = Path(profile["chrome_path"])
        user_data_dir = Path(profile["user_data_dir"])

        if not chrome_path.exists():
            raise FileNotFoundError(f"Không tìm thấy chrome.exe: {chrome_path}")

        user_data_dir.mkdir(parents=True, exist_ok=True)

        args = [
            str(chrome_path),
            f"--remote-debugging-port={profile['port']}",
            f"--user-data-dir={user_data_dir}",
            f"--profile-directory={profile['profile_directory']}",
        ]

        subprocess.Popen(
            args,
            close_fds=True,
            creationflags=getattr(subprocess, "DETACHED_PROCESS", 0),
        )

        return args

    @staticmethod
    def find_free_port(start_port: int, used_ports: set[int] | None = None) -> int:
        used_ports = used_ports or set()
        port = start_port

        while port in used_ports or ChromeLauncher.is_port_open(port):
            port += 1

        return port
