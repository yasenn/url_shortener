import os
from app.storage.postgresql import PostgreSQLURLStorage
from app.services.kafka_service import KafkaClickConsumer

if __name__ == '__main__':
    storage = PostgreSQLURLStorage()
    consumer = KafkaClickConsumer(
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
        storage=storage
    )
    print("Starting click event consumer...")
    consumer.start_consuming()