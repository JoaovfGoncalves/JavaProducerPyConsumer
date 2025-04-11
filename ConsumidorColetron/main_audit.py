import logging
from src.audit_consumer import AuditConsumer

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    consumer = AuditConsumer()
    consumer.start()

if __name__ == "__main__":
    main()
