from kafka import KafkaProducer, KafkaConsumer
import json

class KafkaClickProducer:
    def __init__(self, bootstrap_servers):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    def send_click_event(self, short_code, click_data):
        self.producer.send('click_events', {
            'short_code': short_code,
            'timestamp': click_data['timestamp'],
            'ip': click_data['ip']
        })

class KafkaClickConsumer:
    def __init__(self, bootstrap_servers, storage):
        self.consumer = KafkaConsumer(
            'click_events',
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='earliest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.storage = storage
    
    def start_consuming(self):
        for message in self.consumer:
            try:
                value = message.value
                self.storage.record_click(
                    value['short_code'],
                    {'timestamp': value['timestamp'], 'ip': value['ip']}
                )
            except Exception as e:
                print(f"Error processing message: {str(e)}")