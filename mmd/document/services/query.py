import os
from dotenv import load_dotenv
from pymongo import MongoClient
from document.models import Document
from user.models import MyUser

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))

def get_connection_noSQL():
    db = client[os.getenv("MONGO_DB")]
    collection = db[os.getenv("MONGO_COLLECTION")]
    return collection

def close_connection_noSQL(client_obj):
    # client.close() is usually managed globally or should be handled carefully
    pass

def create_document(title, id_user, content="", file_name="", file_type="", file_size="", version="1.0"):
    try:
        user = MyUser.objects.get(id=id_user)
        doc = Document.objects.create(
            title=title,
            id_user=user,
            content=content,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            version=version,
            status="uploaded"
        )
        return {"success": "Document created successfully", "document_id": doc.id}
    except Exception as e:
        print(f"Error creating document: {e}")
        return {"error": f"Failed to create document: {str(e)}"}

def create_document_noSQL(document_id, context):
    collection = get_connection_noSQL()
    try:
        document_data = Document.objects.filter(id=document_id).first()
        if not document_data:
            return False
            
        if collection.find_one({"document_id": document_id}):
            versione = collection.count_documents({"document_id": document_id}) + 1
        else:
            versione = 1
            
        data = {
            "document_id": document_id,
            "created_at": str(document_data.created_at),
            "content": context,
            "versione": versione
        }
        collection.insert_one(data)  
        return True
    except Exception as e:
        print(f"Error creating NoSQL document: {e}")
        return False    

def get_documents_by_user(id_user):
    # Returning only non-deleted documents
    return Document.objects.filter(id_user_id=id_user, is_deleted=False).order_by('-created_at')

def get_document_by_id(document_id):
    return Document.objects.filter(id=document_id).first()

def update_document_status(document_id, status, id_user):
    try:
        Document.objects.filter(id=document_id, id_user_id=id_user).update(status=status)
        return True
    except Exception as e:
        print(f"Error updating document status: {e}")
        return False
    
def delete_document(document_id, id_user):
    from django.utils import timezone
    try:
        doc = Document.objects.filter(id=document_id, id_user_id=id_user).first()
        if not doc or doc.status == "processing":
            return False
        
        # Soft delete
        doc.is_deleted = True
        doc.deleted_at = timezone.now().date()
        doc.deleted_by = MyUser.objects.get(id=id_user)
        doc.save()
        return True
    except Exception as e:
        print(f"Error deleting document: {e}")
        return False

def get_document_content(document_id):
    collection = get_connection_noSQL()
    try:
        document = collection.find_one({"document_id": document_id}, sort=[("versione", -1)])
        if document:
            return document["content"]
    except Exception as e:
        print(f"Error retrieving document content: {e}")
        return None