import zmq
import json
from django.conf import settings

class ZMQClient:
    """
    Client ZMQ for Django to communicate with the Search Service on PC2.
    Uses REQ/REP pattern.
    """
    def __init__(self, timeout_ms=5000):
        self.server_url = getattr(settings, 'ZMQ_SERVER_URL', 'tcp://192.168.0.49:8000')
        self.timeout_ms = timeout_ms
        self.context = zmq.Context()

    def send_request(self, action, **kwargs):
        """Sends a request to PC2 and waits for a response."""
        socket = self.context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, self.timeout_ms)
        socket.setsockopt(zmq.SNDTIMEO, self.timeout_ms)
        socket.setsockopt(zmq.LINGER, 0)
        
        try:
            socket.connect(self.server_url)
            message = {"action": action}
            message.update(kwargs)
            
            socket.send_json(message)
            return socket.recv_json()
        except zmq.Again:
            return {"status": "error", "message": f"ZMQ Timeout ({self.timeout_ms}ms) - PC2 not responding"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            socket.close()

    def close(self):
        self.context.term()
