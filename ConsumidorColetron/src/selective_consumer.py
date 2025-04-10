import pika
import os
import json
import logging
import time
from datetime import datetime
from config.settings import RABBITMQ_CONFIG, LOG_CONFIG

QUEUE_OPTIONS = {
    "1": ("coletron_urna_cheia", "URNA_CHEIA"),
    "2": ("coletron_capacidade_alerta", "CAPACIDADE_ALERTA")
}

class SelectiveConsumer:
    def __init__(self, queue_name, tipo_mensagem):
        self.queue_name = queue_name
        self.tipo_mensagem = tipo_mensagem
        self.connection = None
        self.channel = None
        self.logger = self._setup_logger()

    def _setup_logger(self):
        os.makedirs("logs", exist_ok=True)
        log_path = os.path.join("logs", f"{self.tipo_mensagem.lower()}.log")

        logger = logging.getLogger(f"{self.tipo_mensagem}_logger")
        logger.setLevel(getattr(logging, LOG_CONFIG['level'], logging.INFO))

        if not logger.handlers:
            file_handler = logging.FileHandler(log_path)
            formatter = logging.Formatter(LOG_CONFIG['format'])
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

    def setup_connection(self):
        credentials = pika.PlainCredentials(
            RABBITMQ_CONFIG['username'], RABBITMQ_CONFIG['password']
        )
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_CONFIG['host'],
            port=RABBITMQ_CONFIG['port'],
            virtual_host=RABBITMQ_CONFIG['virtual_host'],
            credentials=credentials,
            heartbeat=RABBITMQ_CONFIG['heartbeat']
        )

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        self.channel.exchange_declare(
            exchange='coletron_exchange', exchange_type='topic', durable=True
        )
        self.channel.queue_declare(queue=self.queue_name, durable=True)

        routing_key = f"coletron.{self.tipo_mensagem.lower()}"
        self.channel.queue_bind(
            exchange='coletron_exchange',
            queue=self.queue_name,
            routing_key=routing_key
        )
        self.logger.info(f"Conectado à fila '{self.queue_name}' para '{self.tipo_mensagem}' usando routing key '{routing_key}'")

    def callback(self, ch, method, properties, body):
        try:
            message = json.loads(body.decode('utf-8'))
            if message.get("tipo_mensagem") == self.tipo_mensagem:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n[{timestamp}] Mensagem recebida na fila '{self.queue_name}':")
                print(json.dumps(message, indent=2, ensure_ascii=False))
                self.logger.info(f"Mensagem recebida: {json.dumps(message, ensure_ascii=False)}")

        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.setup_connection()
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.callback,
            auto_ack=False
        )
        print(f"Consumidor escutando a fila '{self.queue_name}' (tipo: {self.tipo_mensagem})...")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("\nInterrupção recebida. Encerrando consumidor...")
            self.channel.stop_consuming()
        finally:
            self.connection.close()
            print("Conexão encerrada.")

def menu():
    print("\n=== Seletor de Fila ===")
    print("1. Escutar URNA_CHEIA")
    print("2. Escutar CAPACIDADE_ALERTA")
    escolha = input("Escolha uma fila (1 ou 2): ").strip()
    return QUEUE_OPTIONS.get(escolha)

def run_selective():
    selected = menu()
    if selected:
        fila, tipo = selected
        consumer = SelectiveConsumer(fila, tipo)
        consumer.start_consuming()
    else:
        print("Opção inválida. Encerrando.")

if __name__ == "__main__":
    run_selective()
