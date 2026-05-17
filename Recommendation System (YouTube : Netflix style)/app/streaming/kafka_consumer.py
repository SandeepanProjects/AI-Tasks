from kafka import KafkaConsumer
import json


consumer = KafkaConsumer(
    "recommendation-events",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)


for message in consumer:
    print(message.value)