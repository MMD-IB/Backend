from pymongo import MongoClient

client = MongoClient("mongodb://10.92.133.80:27017/", serverSelectionTimeoutMS=5000)

try:
    client.admin.command("ping")
    print("Connessione riuscita!")
except Exception as e:
    print("Errore di connessione:", e)
