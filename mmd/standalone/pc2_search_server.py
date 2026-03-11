import zmq
import json
import time

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    # Bind to port 8000 on all interfaces
    socket.bind("tcp://*:8000")
    
    print("=" * 50)
    print("  🔎 PC2 ZMQ SEARCH SERVER")
    print("=" * 50)
    print("  📡 Listening on: tcp://*:8000")
    print("  (Waiting for requests from PC1...)")
    
    try:
        while True:
            # Wait for next request from client
            message = socket.recv_json()
            action = message.get("action")
            
            print(f"\n[REQUEST] Action: {action}")
            print(json.dumps(message, indent=2))
            
            # Simulate processing logic
            if action == "search":
                query = message.get("query", "")
                # Mock result
                response = {
                    "status": "ok",
                    "query": query,
                    "results": [
                        {
                            "id": 101,
                            "score": 0.92,
                            "payload": {"file_name": "Report_2024.pdf", "content": f"Risultato pertinente per '{query}' trovato nel testo..."}
                        },
                        {
                            "id": 102,
                            "score": 0.85,
                            "payload": {"file_name": "Dati_Vendita.csv", "content": f"Altro riferimento a '{query}' identificato nelle tabelle..."}
                        }
                    ]
                }
            elif action == "upsert":
                doc_id = message.get("id")
                response = {
                    "status": "ok",
                    "message": f"Documento {doc_id} indicizzato con successo su PC2."
                }
            else:
                response = {"status": "error", "message": f"Azione sconosciuta: {action}"}
            
            # Send reply back to client
            socket.send_json(response)
            print(f"[REPLY] Sent status: {response.get('status')}")

    except KeyboardInterrupt:
        print("\n  👋 Shutting down...")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
