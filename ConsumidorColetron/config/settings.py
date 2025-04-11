RABBITMQ_CONFIG = {
    'host': 'localhost',
    'port': 5672,
    'virtual_host': '/',
    'username': 'coletron',
    'password': 'coletron123',
    'heartbeat': 40000
}

APP_CONFIG = {
    'exchange_name': 'coletron_exchange',
    'queue_name': 'coletron_queue',
    'routing_key': 'coletron.events',
    'consumer_timeout': 40000
}

AUDIT_CONFIG = {
    'exchange_name': 'coletron_exchange',
    'queue_name': 'audit_queue',
    'routing_key': '#'
}

LOG_CONFIG = {
    "filename": "consumer.log",
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
}