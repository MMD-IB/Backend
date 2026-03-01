# from pymongo import MongoClient

# client = MongoClient("mongodb://10.92.133.80:27017/", serverSelectionTimeoutMS=5000)

# try:
#     client.admin.command("ping")
#     print("Connessione riuscita!")
# except Exception as e:
#     print("Errore di connessione:", e)

import zmq
import numpy as np

SERVER_ADDRESS = "tcp://192.168.1.158:8000"
VECTOR_SIZE = 128

def send_request(socket, payload: dict) -> dict:
    socket.send_json(payload)
    return socket.recv_json()

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(SERVER_ADDRESS)
    print(f"Client connesso a {SERVER_ADDRESS}")

    # --- 1. Crea la collection ---
    print("\n[1] Creo la collection...")
    resp = send_request(socket, {"action": "create_collection"})
    print(resp)

    # --- 2. Inserisci alcuni punti ---
    print("\n[2] Inserisco punti...")
    for i in range(1, 4):
        resp = send_request(socket, {
            "action": "upsert",
            "id": i,
            "content": f"Questo è il documento numero {i}"
        })
        print(resp)

    # --- 3. Leggi un punto per ID ---
    print("\n[3] Leggo il punto con id=2...")
    resp = send_request(socket, {"action": "get", "id": 2})
    print(resp)

    # --- 4. Cerca per similarità ---
    print("\n[4] Cerco punti simili...")
    query_vector = np.random.rand(VECTOR_SIZE).tolist()
    resp = send_request(socket, {
        "action": "search",
        "vector": query_vector,
        "limit": 3
    })
    print(resp)

    # --- 5. Elimina un punto ---
    print("\n[5] Elimino il punto con id=1...")
    resp = send_request(socket, {"action": "delete", "id": 1})
    print(resp)

    # --- 6. Verifica che sia stato eliminato ---
    print("\n[6] Verifico che il punto 1 non esista più...")
    resp = send_request(socket, {"action": "get", "id": 1})
    print(resp)

    socket.close()
    context.term()

if __name__ == "__main__":
    main()