# # # #
# # # #   Hello World client in Python
# # # #   Connects REQ socket to tcp://localhost:5555
# # # #   Sends "Hello" to server, expects "World" back
# # # #
# # # import zmq
# # # context = zmq.Context()

# # # #  Socket to talk to server
# # # print("Connecting to hello world server…")
# # # socket = context.socket(zmq.REQ)
# # # socket.connect("tcp://192.168.0.127:8000")

# # # #  Do 10 requests, waiting each time for a response
# # # for request in range(10):
# # #     print("Sending request %s …" % request)
# # #     socket.send(b"Matteo is gay")

# # #     #  Get the reply.
# # #     message = socket.recv()
# # #     print("Received reply %s [ %s ]" % (request, message))


# import os
# import psycopg2
# from dotenv import load_dotenv
# from pymongo import MongoClient

# load_dotenv()


# conn = psycopg2.connect(
#     dbname=os.getenv("DB_NAME"),
#     user=os.getenv("DB_USER"),
#     password=os.getenv("DB_PASSWORD"),
#     host=os.getenv("DB_HOST"),   # IP PC DB
#     port=os.getenv("DB_PORT")
# )

# cur = conn.cursor()


# # CREATE

# query = """
# INSERT INTO users (nome, cognome, email, password_hash)
# VALUES (%s, %s, %s, %s)
# """

# cur.execute(query, (
#     "Giuseppe",
#     "Verdi",
#     "giuseppe.verdi@email.it",
#     "password123"
# ))


# # # READ
# query="SELECT * FROM users"
# cur.execute(query)

# rows = cur.fetchall()
# for row in rows:
#     print(row)
    
    
# # # UPDATE
# # # query = "UPDATE users SET nome=%s WHERE id_user=%s"

# # # cur.execute(query,(
# # #     "Valentino",
# # #     1
# # # ))

# # DELETE

# # query = "DELETE FROM users WHERE id_user=%s"
# # cur.execute(query,(
# #     7,
# # ))

# # print(cur.rowcount, "record(s) deleted")


# client = MongoClient(os.getenv("MONGO_URI"))
# db = client[os.getenv("MONGO_DB")]
# collection = db[os.getenv("MONGO_COLLECTION")]



# # CREATE
# doc = {
#     "nome": "Giuseppe",
#     "cognome": "Verdi",
#     "eta": 25
# }
# collection.insert_one(doc)

# # # READ
# # # for doc in collection.find():
# # #     print(doc)

# # # UPDATE
# # # query = {"nome": "Giovanni"}
# # # new_values = {"$set": {"eta": 26}}
# # # collection.update_one(query, new_values)

# # # DELETE
# # # query = {"nome": "Giovanni"}
# # # collection.delete_one(query)

# conn.commit()

# cur.close()
# conn.close()

# client.close()

# print("Utente inserito con successo")
