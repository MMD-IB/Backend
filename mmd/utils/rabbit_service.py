import pika
import json
from django.conf import settings

class RabbitProducer:
    """
    Service to send messages to RabbitMQ.
    Usage:
        producer = RabbitProducer()
        producer.send_message("notifications.info", {"message": "Hello!"})
    """
    def __init__(self):
        self.host = getattr(settings, 'RABBITMQ_HOST', 'localhost')
        self.port = getattr(settings, 'RABBITMQ_PORT', 5672)
        self.user = getattr(settings, 'RABBITMQ_USER', 'guest')
        self.password = getattr(settings, 'RABBITMQ_PASSWORD', 'guest')
        self.exchange = getattr(settings, 'RABBITMQ_EXCHANGE', 'mmd_exchange')

    def _get_connection(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials
        )
        return pika.BlockingConnection(parameters)

    def send_message(self, routing_key, message_dict):
        """Sends a JSON-serializable dict to the specified routing key."""
        try:
            connection = self._get_connection()
            channel = connection.channel()

            # Ensure exchange exists
            channel.exchange_declare(
                exchange=self.exchange,
                exchange_type='topic',
                durable=True
            )

            message_body = json.dumps(message_dict)
            
            channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
            
            connection.close()
            return True
        except Exception as e:
            print(f"RabbitMQ Error: {e}")
            return False
