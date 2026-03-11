import pika
import json
import sys
import os
from dotenv import load_dotenv

# Load config from .env if available
load_dotenv()

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', 'mmd_exchange')

def callback(ch, method, properties, body):
    routing_key = method.routing_key
    try:
        data = json.loads(body)
        print(f"\n[RECEIVED] Topic: {routing_key}")
        print(json.dumps(data, indent=2))
        print("-" * 30)
    except Exception as e:
        print(f"Error parsing message: {e}")

def main():
    print("=" * 50)
    print("  🐰 RabbitMQ Notification Consumer (PC2 Simulator)")
    print("=" * 50)
    
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Declare exchange
        channel.exchange_declare(
            exchange=RABBITMQ_EXCHANGE,
            exchange_type='topic',
            durable=True
        )

        # Create temporary queue
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        # Bind to relevant topics
        topics = ["notifications.#", "search.#"]
        for topic in topics:
            channel.queue_bind(
                exchange=RABBITMQ_EXCHANGE,
                queue=queue_name,
                routing_key=topic
            )

        print(f" [*] Connected to {RABBITMQ_HOST}")
        print(f" [*] Waiting for notifications. To exit press CTRL+C")
        
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=True
        )

        channel.start_consuming()

    except KeyboardInterrupt:
        print("\n  👋 Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
