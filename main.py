# # # # #
# # # # #   Hello World client in Python
# # # # #   Connects REQ socket to tcp://localhost:5555
# # # # #   Sends "Hello" to server, expects "World" back
# # # # #
# # # # import zmq
# # # # context = zmq.Context()

# # # # #  Socket to talk to server
# # # # print("Connecting to hello world server…")
# # # # socket = context.socket(zmq.REQ)
# # # # socket.connect("tcp://192.168.0.127:8000")

# # # # #  Do 10 requests, waiting each time for a response
# # # # for request in range(10):
# # # #     print("Sending request %s …" % request)
# # # #     socket.send(b"Matteo is gay")

# # # #     #  Get the reply.
# # # #     message = socket.recv()
# # # #     print("Received reply %s [ %s ]" % (request, message))


import os
# import psycopg2
# from dotenv import load_dotenv
# from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

# load_dotenv()


# conn = psycopg2.connect(
#     dbname=os.getenv("DB_NAME"),
#     user=os.getenv("DB_USER"),
#     password=os.getenv("DB_PASSWORD"),
#     host=os.getenv("DB_HOST"),   # IP PC DB
#     port=os.getenv("DB_PORT")
# )

# cur = conn.cursor()


# # # CREATE

# # query = """
# # INSERT INTO users (name, surname, email, password_hash)
# # VALUES (%s, %s, %s, %s)
# # """

# # cur.execute(query, (
# #     "Giuseppe",
# #     "Verdi",
# #     "giuseppe.verdi@email.it",
# #     "password123"
# # ))


# # # # READ
# # query="SELECT * FROM users"
# # cur.execute(query)

# # rows = cur.fetchall()
# # for row in rows:
# #     print(row)
    
    
# # # # UPDATE
# # # # query = "UPDATE users SET nome=%s WHERE id_user=%s"

# # # # cur.execute(query,(
# # # #     "Valentino",
# # # #     1
# # # # ))

# # # DELETE

# # query = "DELETE FROM users WHERE email=%s"
# # cur.execute(query,(
# #     "giuseppe.verdi@email.it",
# # ))

# # print(cur.rowcount, "record(s) deleted")


# client = MongoClient(os.getenv("MONGO_URI"))
# db = client[os.getenv("MONGO_DB")]
# collection = db[os.getenv("MONGO_COLLECTION")]



# # # CREATE
# doc = {
#     "nome": "Giuseppe",
#     "cognome": "Verdi",
#     "eta": 25
# }
# collection.insert_one(doc)

# # # # READ
# # # # for doc in collection.find():
# # # #     print(doc)

# # # # UPDATE
# # # # query = {"nome": "Giovanni"}
# # # # new_values = {"$set": {"eta": 26}}
# # # # collection.update_one(query, new_values)

# # # # DELETE
# # # # query = {"nome": "Giovanni"}
# # # # collection.delete_one(query)

# conn.commit()

# cur.close()
# conn.close()

# client.close()

# print("Utente inserito con successo")



### --------------------- DB VETTORIALE ---------------------####  

# DB_PATH = os.getenv("DB_PATH")
# COLLECTION = os.getenv("COLLECTION")
# VECTOR_SIZE = os.getenv("VECTOR_SIZE")

# model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# client = QdrantClient(path=DB_PATH)

# # FIX 1: sostituisce recreate_collection (deprecata)
# if client.collection_exists(COLLECTION):
#     client.delete_collection(COLLECTION)

# client.create_collection(
#     collection_name=COLLECTION,
#     vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
# )

# point_id = 5   
# text = "la palla corre"

# vector = model.encode(text).tolist()

# client.upsert(
#     collection_name=COLLECTION,
#     points=[PointStruct(id=point_id, vector=vector, payload={"content": text})]
# )

# query_text = "il pc non funziona"
# query_vector = model.encode(query_text).tolist()

# result = client.query_points(
#     collection_name=COLLECTION,
#     query=query_vector,
#     limit=10
# )

# for res in result.points:
#     print(f"Risultato: {res.payload['content']} (Score: {round(res.score, 3)})")

# # FIX 2: chiusura esplicita del client per evitare l'errore msvcrt
# client.close()