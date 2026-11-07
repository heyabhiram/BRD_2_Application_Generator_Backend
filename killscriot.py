
import subprocess

START_PORT = 2999
END_PORT = 5000

def kill_processes_on_ports():
    result = subprocess.run(
        ["netstat", "-ano", "-p", "tcp"],
        capture_output=True,
        text=True
    )

    killed_pids = set()

    for line in result.stdout.splitlines():
        parts = line.split()

        if len(parts) < 5:
            continue

        local_address = parts[1]
        state = parts[3]
        pid = parts[4]

        if state != "LISTENING":
            continue

        try:
            port = int(local_address.rsplit(":", 1)[1])
            pid = int(pid)
        except (ValueError, IndexError):
            continue

        if START_PORT <= port <= END_PORT and pid not in killed_pids:
            print(f"Killing PID {pid} on port {port}...")

            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                capture_output=True,
                text=True
            )

            killed_pids.add(pid)

    if not killed_pids:
        print("No listening processes found in the specified port range.")
    else:
        print(f"\nTerminated {len(killed_pids)} process(es).")


if __name__ == "__main__":
    kill_processes_on_ports()
