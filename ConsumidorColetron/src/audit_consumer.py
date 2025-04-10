import pika
import json
import time
import os
import signal
from datetime import datetime
import logging
from config.settings import RABBITMQ_CONFIG, AUDIT_CONFIG

class AuditConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.logger = logging.getLogger("Auditoria")
        self.should_stop = False
        self.start_time = None

    def setup_connection(self):
        credentials = pika.PlainCredentials(RABBITMQ_CONFIG['username'], RABBITMQ_CONFIG['password'])
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
            exchange=AUDIT_CONFIG['exchange_name'],
            exchange_type='topic',
            durable=True
        )
        self.channel.queue_declare(
            queue=AUDIT_CONFIG['queue_name'],
            durable=True
        )
        self.channel.queue_bind(
            exchange=AUDIT_CONFIG['exchange_name'],
            queue=AUDIT_CONFIG['queue_name'],
            routing_key=AUDIT_CONFIG['routing_key']
        )

        self.logger.info(f"[AUDITORIA] Conectado à fila '{AUDIT_CONFIG['queue_name']}'")

    def callback(self, ch, method, properties, body):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            message = json.loads(body)
            formatted = json.dumps(message, ensure_ascii=False)

            print(f"\n[{timestamp}] [AUDITORIA] Mensagem recebida:")
            print(json.dumps(message, indent=2, ensure_ascii=False))

            os.makedirs("logs", exist_ok=True)
            with open("logs/auditoria_mensagens.log", "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {formatted}\n")

            self.logger.info("Mensagem registrada no log de auditoria.")

        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem de auditoria: {e}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def stop_consuming(self):
        if self.channel and self.channel.is_open:
            self.channel.stop_consuming()
        if self.connection and self.connection.is_open:
            self.connection.close()
        self.logger.info("Conexões de auditoria encerradas.")

    def signal_handler(self, sig, frame):
        print("\nInterrupção recebida. Encerrando auditoria...")
        self.should_stop = True
        self.stop_consuming()

    def start(self, timeout=10):
        self.setup_connection()

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.channel.basic_consume(
            queue=AUDIT_CONFIG['queue_name'],
            on_message_callback=self.callback,
            auto_ack=False
        )

        print("Auditoria em escuta...")
        self.start_time = time.time()

        while not self.should_stop:
            self.connection.process_data_events(time_limit=1)
            if time.time() - self.start_time >= timeout:
                print("Tempo de escuta encerrado. Encerrando auditoria...")
                break

        self.stop_consuming()


def run_audit():
    consumer = AuditConsumer()
    consumer.start()
