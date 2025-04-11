import argparse
import subprocess
import sys
import os
import time
from multiprocessing import Process

def start_worker(worker_id, mode):
    env = os.environ.copy()
    env["WORKER_ID"] = str(worker_id)

    target_script = "main.py"
    print(f"Iniciando consumidor {worker_id} no modo {mode} com script {target_script}")
    subprocess.run([sys.executable, target_script], env=env)

def run_consumers(workers=1, mode="standard"):
    processes = []
    for i in range(1, workers + 1):
        p = Process(target=start_worker, args=(i, mode))
        p.start()
        processes.append(p)
        time.sleep(0.5)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\nInterrupção recebida. Encerrando consumidores...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()

def main():
    parser = argparse.ArgumentParser(description="Executor de múltiplos consumidores")
    parser.add_argument("--workers", type=int, default=1, help="Número de consumidores")
    parser.add_argument("--mode", choices=["standard", "broadcast"], default="standard", help="Modo de operação")

    args = parser.parse_args()
    run_consumers(args.workers, args.mode)

if __name__ == "__main__":
    main()