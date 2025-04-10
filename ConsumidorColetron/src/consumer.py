import pika
import time
import logging
import signal
from datetime import datetime
from config.settings import RABBITMQ_CONFIG, APP_CONFIG
from src.message_handler import MessageHandler

class ColetronConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.should_stop = False
        self.start_time = None
        self.logger = logging.getLogger(__name__)
        self.message_handler = MessageHandler()

    def setup_connection(self):
        """Configura a conexão com o RabbitMQ"""
        credentials = pika.PlainCredentials(
            RABBITMQ_CONFIG['username'], 
            RABBITMQ_CONFIG['password']
        )
        
        connection_params = pika.ConnectionParameters(
            host=RABBITMQ_CONFIG['host'],
            port=RABBITMQ_CONFIG['port'],
            virtual_host=RABBITMQ_CONFIG['virtual_host'],
            credentials=credentials,
            heartbeat=RABBITMQ_CONFIG['heartbeat']
        )
        
        self.connection = pika.BlockingConnection(connection_params)
        self.channel = self.connection.channel()
        
        # Declarações de exchange e fila
        self.channel.exchange_declare(
            exchange=APP_CONFIG['exchange_name'],
            exchange_type='topic',
            durable=True
        )
        
        self.channel.queue_declare(
            queue=APP_CONFIG['queue_name'], 
            durable=True
        )
        
        self.channel.queue_bind(
            exchange=APP_CONFIG['exchange_name'],
            queue=APP_CONFIG['queue_name'],
            routing_key=APP_CONFIG['routing_key']
        )
        
        self.logger.info(f"Conexao estabelecida com RabbitMQ em {RABBITMQ_CONFIG['host']}")

    def process_message(self, ch, method, properties, body):
        """Callback para processar cada mensagem recebida"""
        try:
            self.message_handler.handle(ch, method, properties, body)
            
            elapsed_time = time.time() - self.start_time
            if elapsed_time >= APP_CONFIG['consumer_timeout']:
                self.logger.info(f"Tempo limite de {APP_CONFIG['consumer_timeout']} segundos atingido. Encerrando consumidor...")
                self.should_stop = True
                self.connection.add_callback_threadsafe(lambda: self.channel.stop_consuming())
                
        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem: {e}")
            # Acknowledge mesmo em caso de erro para não bloquear a fila
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        """Inicia o consumo de mensagens da fila"""
        try:
            self.setup_connection()
            self.start_time = time.time()
            
            self.logger.info(f"Iniciando consumidor para a fila '{APP_CONFIG['queue_name']}'")
            self.logger.info(f"Ouvindo mensagens por {APP_CONFIG['consumer_timeout']} segundos...")
            
            # Configura o modo de consumo
            self.channel.basic_qos(prefetch_count=1)
            
            # Inicia o consumo
            self.channel.basic_consume(
                queue=APP_CONFIG['queue_name'],
                on_message_callback=self.process_message,
                auto_ack=False
            )
            
            # Configura handler para CTRL+C
            def signal_handler(sig, frame):
                self.logger.info("Interrupção recebida. Encerrando graciosamente...")
                self.should_stop = True
                if self.channel:
                    self.channel.stop_consuming()
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Inicia o loop de consumo
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            self.logger.info("Interrupção recebida. Encerrando...")
            self.should_stop = True
        except Exception as e:
            self.logger.error(f"Erro ao iniciar o consumidor: {e}")
            self.should_stop = True
        finally:
            self.close_connection()

    def close_connection(self):
        """Fecha a conexão com o RabbitMQ"""
        try:
            if self.channel and self.channel.is_open:
                if hasattr(self.channel, 'is_consuming') and self.channel.is_consuming():
                    self.channel.stop_consuming()
                self.channel.close()
                
            if self.connection and self.connection.is_open:
                self.connection.close()
                
            self.logger.info("Conexões fechadas com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao fechar conexões: {e}")