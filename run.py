"""Unified launcher for Smart Task Manager (FastAPI + Streamlit)."""
import argparse
import os
import signal
import subprocess
import sys
import time

def start_api(host: str = "127.0.0.1", port: int = 8000):
    """Start FastAPI server with uvicorn."""
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", host,
        "--port", str(port),
        "--reload"
    ]
    print(f"[*] Starting FastAPI server on http://{host}:{port} (Docs: http://{host}:{port}/docs)...")
    return subprocess.Popen(cmd)

def start_ui(port: int = 8501):
    """Start Streamlit UI dashboard."""
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "ui/streamlit_app.py",
        "--server.port", str(port),
        "--server.headless", "true",
        "--theme.base", "dark"
    ]
    print(f"[*] Starting Streamlit Dashboard on http://localhost:{port}...")
    return subprocess.Popen(cmd)

def main():
    parser = argparse.ArgumentParser(description="Smart Task Manager Unified Runner")
    parser.add_argument("--api-only", action="store_true", help="Launch FastAPI REST backend only")
    parser.add_argument("--ui-only", action="store_true", help="Launch Streamlit UI only")
    parser.add_argument("--test", action="store_true", help="Run pytest test suite")
    parser.add_argument("--host", default="127.0.0.1", help="API host (default: 127.0.0.1)")
    parser.add_argument("--api-port", type=int, default=8000, help="API port (default: 8000)")
    parser.add_argument("--ui-port", type=int, default=8501, help="UI port (default: 8501)")
    args = parser.parse_args()

    if args.test:
        print("[TEST] Running test suite...")
        res = subprocess.run([sys.executable, "-m", "pytest", "-v"])
        sys.exit(res.returncode)

    processes = []
    try:
        if args.api_only:
            proc = start_api(host=args.host, port=args.api_port)
            processes.append(proc)
        elif args.ui_only:
            proc = start_ui(port=args.ui_port)
            processes.append(proc)
        else:
            # Full stack concurrent execution
            api_proc = start_api(host=args.host, port=args.api_port)
            processes.append(api_proc)
            time.sleep(1.5)  # Allow API to initialize tables
            ui_proc = start_ui(port=args.ui_port)
            processes.append(ui_proc)

            print("\n" + "=" * 60)
            print("SMART TASK MANAGER IS RUNNING!")
            print(f" - Interactive UI:    http://localhost:{args.ui_port}")
            print(f" - API Documentation: http://{args.host}:{args.api_port}/docs")
            print(f" - Health Check:       http://{args.host}:{args.api_port}/")
            print("=" * 60)
            print("Press Ctrl+C to stop all services.\n")

        # Keep alive and monitor child processes
        while True:
            for p in processes:
                if p.poll() is not None:
                    print(f"Process {p.pid} terminated unexpectedly.")
                    return
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[*] Shutting down services safely...")
    finally:
        for p in processes:
            try:
                p.terminate()
                p.wait(timeout=3)
            except Exception:
                p.kill()
        print("[OK] All services stopped.")

if __name__ == "__main__":
    main()
