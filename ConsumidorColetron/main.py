import logging
import sys
import time
import os
from config.settings import LOG_CONFIG
from src.consumer import ColetronConsumer

def setup_logging(worker_id):
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOG_CONFIG['level'], logging.INFO))

    log_filename = os.path.join("logs", LOG_CONFIG['filename'].replace(".log", f"_worker{worker_id}.log"))

    if not logger.handlers:
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(logging.Formatter(LOG_CONFIG['format']))
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(LOG_CONFIG['format']))
        logger.addHandler(console_handler)

def main():
    worker_id = os.getenv("WORKER_ID", "main")
    pid = os.getpid()

    print(f"\nColetron RabbitMQ Consumer (Worker ID: {worker_id}, PID: {pid})")
    print("-------------------------------------------------------------")

    setup_logging(worker_id)
    logger = logging.getLogger(__name__)

    logger.info(f"Iniciando consumidor com ID: {worker_id} | PID: {pid}")
    print(f"[Worker {worker_id}] iniciado com PID {pid}")

    consumer = ColetronConsumer()

    try:
        consumer.start_consuming()
    except Exception as e:
        logger.exception(f"Erro na execução do consumidor {worker_id}")
        sys.exit(1)

    elapsed = time.time() - consumer.start_time if consumer.start_time else 0
    logger.info(f"Consumidor {worker_id} finalizado após {elapsed:.1f} segundos")
    print(f"\nConsumidor {worker_id} finalizado após {elapsed:.1f} segundos")

if __name__ == "__main__":
    main()
