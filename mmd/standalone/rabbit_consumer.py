import pika
import json
import sys
import os
from dotenv import load_dotenv

# Load config from .env if available
load_dotenv()

# Setup Django Environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mmd.settings')
import django
django.setup()

from utils.models import Notification
from user.models import MyUser

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
        print(f" [DEBUG] Message body: {body.decode()}")
        
        # Handle notifications
        if routing_key.startswith("notifications."):
            status = data.get("status")
            user_id = data.get("user_id")
            file_name = data.get("file_name", "Unknown")
            
            try:
                user = MyUser.objects.get(id=user_id)
                message = ""
                
                if status == "processing_started":
                    message = f"Documento '{file_name}' in fase di caricamento"
                elif status == "success":
                    message = f"File '{file_name}' caricato e indicizzato con successo."
                
                if message:
                    Notification.objects.create(id_user=user, message=message)
                    print(f" [DB] Created notification for user {user_id}: {message}")
            except MyUser.DoesNotExist:
                print(f" [ERR] User {user_id} not found")
            except Exception as e:
                print(f" [ERR] Failed to create notification: {e}")

        print(json.dumps(data, indent=2))
        print("-" * 30)
    except Exception as e:
        print(f"Error parsing message: {e}")

def main():
    print("=" * 50)
    print("  RabbitMQ Notification Consumer (PC2 Simulator)")
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
        print("\n  Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n  Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
