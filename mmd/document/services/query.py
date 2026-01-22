import os
import psycopg
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))

def get_connection():
    return psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    
def get_connection_noSQL():
    db = client[os.getenv("MONGO_DB")]
    collection = db[os.getenv("MONGO_COLLECTION")]
    return collection

def close_connection_noSQL(client):
    client.close()
    

def create_document(title,id_user):
    conn = get_connection()
    cur = conn.cursor()
    
    query = "INSERT INTO documents (title, id_user, status, created_at) VALUES (%s, %s, %s, CURRENT_DATE) RETURNING id"
    try:
        cur.execute(query, (title,id_user,"uploaded"))
        document_id = cur.fetchone()[0]
        conn.commit()
        return {"success": "Document created successfully", "document_id": document_id}
    except Exception as e:
        print(f"Error creating document: {e}")
        return {"error": "Failed to create document"}
    finally:
        cur.close()
        conn.close()

def create_document_noSQL(document_id, context):
    collection = get_connection_noSQL()
    try:
        document = get_document_by_id(document_id)
        if collection.find_one({"document_id": document_id}):
            versione = collection.count_documents({"document_id": document_id})+1
        else:
            versione = 1
        if document:
            data = {
                "document_id": document[0],
                "created_at": document[3],
                "content": context,
                "versione": versione
            }
            collection.insert_one(data)  
            return True
    except Exception as e:
        print(f"Error creating NoSQL document: {e}")
        return False    
    finally:
        close_connection_noSQL(client)
        

def get_documents_by_user(id_user):
    conn = get_connection()
    cur = conn.cursor()
    
    query = "SELECT id, title, status, created_at FROM documents WHERE id_user=%s"
    cur.execute(query, (id_user,))
    documents = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return documents

def get_document_by_id(document_id):
    conn = get_connection()
    cur = conn.cursor()
    
    query = "SELECT id, title, status, created_at FROM documents WHERE id=%s"
    cur.execute(query, (document_id,))
    document = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return document

def update_document_status(document_id, status,id_user):
    conn = get_connection()
    cur = conn.cursor()
    
    query = "UPDATE documents SET status=%s WHERE id=%s AND id_user=%s"
    try:
        cur.execute(query, (status, document_id, id_user))  
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating document status: {e}")
        return False
    finally:
        cur.close()
        conn.close()
    
def delete_document(document_id,id_user):
    conn = get_connection()
    cur = conn.cursor()
    
    document= get_document_by_id(document_id)
    if document.status != "processing":
        return False
    query = "DELETE FROM documents WHERE id=%s AND id_user=%s"
    try:
        cur.execute(query, (document_id, id_user))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting document: {e}")
        return False
    finally:
        cur.close()
        conn.close()
        
        
def get_document_content(document_id):
    collection = get_connection_noSQL()
    try:
        document = collection.find_one({"document_id": document_id}, sort=[("versione", -1)])
        if document:
            return document["content"]
    except Exception as e:
        print(f"Error retrieving document content: {e}")
        return None
    finally:
        close_connection_noSQL(client)