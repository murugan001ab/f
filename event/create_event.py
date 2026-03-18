from confluent_kafka import Producer
import json

conf = {
    "bootstrap.servers": "kafka-1520026d-murugan001ab-05f5.k.aivencloud.com:11609",
    "security.protocol": "SSL",
    "ssl.ca.location": "ca.pem",
    "ssl.certificate.location": "service.cert",
    "ssl.key.location": "service.key"
}

producer = Producer(conf)


def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Event delivered to {msg.topic()} [{msg.partition()}]")


def create_user_event(user_id: int) -> bool:
    try:

        event = {
            "event_type": "user_created",
            "user_id": user_id
        }

        producer.produce(
            topic="user",
            value=json.dumps(event),
            callback=delivery_report
        )

        producer.poll(0)

        print("helo")

        return True

    except Exception as e:
        print("Kafka Error:", e)
        return False