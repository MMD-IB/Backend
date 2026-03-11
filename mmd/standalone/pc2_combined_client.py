import pika
import zmq
import json
import threading
import os
import sys
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()

# RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', '192.168.0.49')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASSWORD', 'guest')
RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', 'mmd_exchange')

# ZMQ (Search Server)
SERVER_HOST = os.getenv('SERVER_HOST', 'localhost')
SERVER_PORT = os.getenv('SERVER_PORT', '8000')
ZMQ_URL = f"tcp://{SERVER_HOST}:{SERVER_PORT}"

# --- RABBITMQ CONSUMER (Thread) ---
def rabbit_worker():
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()

        channel.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type='topic', durable=True)
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange=RABBITMQ_EXCHANGE, queue=queue_name, routing_key="notifications.#")
        channel.queue_bind(exchange=RABBITMQ_EXCHANGE, queue=queue_name, routing_key="search.#")

        def callback(ch, method, properties, body):
            data = json.loads(body)
            print(f"\n\n🔔 [NOTIFICATION] {method.routing_key}: {json.dumps(data, indent=2)}")
            print("query> ", end="", flush=True)

        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except Exception as e:
        print(f"\n❌ RabbitMQ Error: {e}")

# --- ZMQ SEARCH (Main) ---
def search(query):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.RCVTIMEO, 5000)
    socket.connect(ZMQ_URL)
    
    try:
        socket.send_json({"action": "search", "query": query})
        response = socket.recv_json()
        return response
    except zmq.Again:
        return {"status": "error", "message": "Search server timeout"}
    finally:
        socket.close()
        context.term()

def main():
    print("=" * 60)
    print("  🚀 PC2 UNIFIED CLIENT: Semantic Search + Real-time Notifications")
    print("=" * 60)
    print(f"  📡 Search Server: {ZMQ_URL}")
    print(f"  🐰 RabbitMQ:      {RABBITMQ_HOST}")
    print("-" * 60)

    # Start RabbitMQ thread
    t = threading.Thread(target=rabbit_worker, daemon=True)
    t.start()

    print("\n  Commands: type your query to search. Type ':quit' to exit.\n")

    try:
        while True:
            query = input("query> ").strip()
            if not query: continue
            if query == ":quit": break

            print("  🔍 Searching...")
            res = search(query)
            
            if res.get("status") == "ok":
                results = res.get("results", [])
                print(f"  ✅ Found {len(results)} results:")
                for i, r in enumerate(results, 1):
                    print(f"     {i}. [Score: {r['score']:.4f}] {r['payload'].get('content', '')[:100]}...")
            else:
                print(f"  ❌ Error: {res.get('message', 'Unknown error')}")
            
            print()

    except KeyboardInterrupt:
        print("\n\n  👋 Exiting...")

if __name__ == "__main__":
    main()
