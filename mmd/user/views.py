import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone
from .models import MyUser
from document.models import Document
from document.services.query import (
    get_documents_by_user,
    delete_document,
    update_document_status,
    create_document,
    create_document_noSQL,
    get_document_content
)
from utils.models import Notification
from utils.rabbit_service import RabbitProducer
from utils.zmq_service import ZMQClient

def get_user(request):
    user_id = request.session.get("id_user")
    if not user_id:
        return None
    try:
        return MyUser.objects.filter(id=user_id).first()
    except Exception as e:
        print("Errore nel recupero utente:", e)
        return None

def dashboard_view(request):
    user = get_user(request)
    if not user:
        return redirect("index")
    
    docs = get_documents_by_user(user.id)
    total_files = docs.count()
    
    # Calculate total space used (assuming file_size is a string like "12.34 KB")
    total_kb = 0
    for doc in docs:
        try:
            size_str = doc.file_size.split(' ')[0]
            total_kb += float(size_str)
        except:
            pass
    
    space_used = f"{total_kb / 1024:.2f} MB" if total_kb > 1024 else f"{total_kb:.2f} KB"
    
    last_doc = docs.first()
    last_embedding_date = last_doc.created_at if last_doc else None

    context = {
        "user": user,
        "total_files": total_files,
        "space_used": space_used,
        "last_embedding_date": last_embedding_date,
        "recent_documents": docs[:5]
    }
    return render(request, "user/dashboard.html", context)

def file_manager_view(request):
    user = get_user(request)
    if not user:
        return redirect("index")
    
    if request.method == "POST":
        azione = request.POST.get("azione")
        doc_id = request.POST.get("document_id")
        
        if azione == "delete":
            delete_document(doc_id, user.id)
            if request.headers.get('HX-Request'):
                response = HttpResponse("") 
                response['HX-Toast'] = "Documento eliminato correttamente."
                return response
        
        elif azione == "toggle_search":
            status = request.POST.get("status")
            update_document_status(doc_id, status, user.id)
            if request.headers.get('HX-Request'):
                 return HttpResponse("Success")

    docs = get_documents_by_user(user.id)
    context = {"user": user, "documents": docs}
    return render(request, "user/file_manager.html", context)

def upload_center_view(request):
    user = get_user(request)
    if not user:
        return redirect("index")
    
    if request.method == "POST":
        azione = request.POST.get("azione")
        if azione == "create_document":
            title = request.POST.get("title")
            file = request.FILES.get("file_upload")

            # Initialize RabbitProducer
            producer = RabbitProducer()
            producer.send_message("notifications.info", {
                "status": "processing_started",
                "user_id": user.id,
                "file_name": file.name if file else "Unknown"
            })
            
            if not file:
                return HttpResponse("File missing", status=400)

            # Extract metadata
            file_name = file.name
            file_type = os.path.splitext(file_name)[1]
            file_size = f"{file.size / 1024:.2f} KB"
            
            try:
                contenuto = file.read().decode("utf-8")
                
                extra = create_document(
                    title=title,
                    id_user=user.id,
                    file_name=file_name,
                    file_type=file_type,
                    file_size=file_size
                )

                if extra.get("success"):
                    document_id = extra.get("document_id")
                    
                    # Notify PC2 via ZMQ to index the new document
                    zmq_client = ZMQClient()
                    zmq_client.send_request("upsert", 
                        id=document_id, 
                        content=contenuto, 
                        user_id=user.id,
                        file_name=file_name
                    )

                    create_document_noSQL(document_id, contenuto)
                    
                    # Create Notification
                    Notification.objects.create(
                        id_user=user,
                        message=f"File '{file_name}' caricato e indicizzato con successo."
                    )
                    
                    # Notify success via RabbitMQ
                    producer.send_message("notifications.info", {
                        "status": "success",
                        "user_id": user.id,
                        "file_name": file_name,
                        "document_id": document_id
                    })
                    
                    response = HttpResponse('<div class="alert alert-success mt-4">Caricamento completato!</div>')
                    response['HX-Toast'] = "Documento caricato con successo!"
                    return response
                else:
                    return HttpResponse(f"Errore: {extra.get('error')}", status=500)
            except Exception as e:
                return HttpResponse(f"Errore: {str(e)}", status=500)

    context = {"user": user}
    return render(request, "user/upload_center.html", context)

def semantic_search_view(request):
    user = get_user(request)
    if not user:
        return redirect("index")
    
    query = request.GET.get("q", "")
    results = []
    if query:
        # Notify search activity via RabbitMQ
        producer = RabbitProducer()
        producer.send_message("search.activity", {
            "user_id": user.id,
            "query": query,
            "timestamp": str(timezone.now())
        })

        # Call the semantic search service on PC2 via ZMQ
        zmq_client = ZMQClient()
        response = zmq_client.send_request("search", query=query, user_id=user.id, limit=5)
        
        if response.get("status") == "ok":
            for r in response.get("results", []):
                results.append({
                    "doc": {"title": r["payload"].get("file_name", "Documento"), "created_at": None},
                    "snippet": r["payload"].get("content", "")[:200] + "...",
                    "score": f"{int(r['score'] * 100)}%"
                })
        else:
            # Fallback to local search if ZMQ fails or returns error
            docs = get_documents_by_user(user.id, query=query)
            for doc in docs:
                results.append({
                    "doc": doc,
                    "snippet": doc.content[:200] + "...",
                    "score": "N/A"
                })

    context = {"user": user, "query": query, "results": results}
    return render(request, "user/semantic_search.html", context)

def notifications_view(request):
    user = get_user(request)
    if not user:
        return redirect("index")
    
    notifications = Notification.objects.filter(id_user=user).order_by('-notification_date')
    context = {"user": user, "notifications": notifications}
    return render(request, "user/notifications.html", context)

def notification_dropdown(request):
    user = get_user(request)
    if not user:
        return HttpResponseForbidden()
    
    notifications = Notification.objects.filter(id_user=user).order_by('-notification_date')[:5]
    context = {"notifications": notifications}
    return render(request, "user/fragments/notification_dropdown.html", context)

def document_preview(request, document_id):
    user = get_user(request)
    if not user:
        return HttpResponseForbidden()
    
    doc = get_object_or_404(Document, id=document_id, id_user=user)
    content = get_document_content(document_id)
    
    context = {
        "document": doc,
        "content": content
    }
    return render(request, "user/fragments/document_preview.html", context)

def update_user(request):
    user_id = request.session.get("id_user")
    if not user_id:
        return {"error": "User not logged in."}
    
    try:
        user = get_object_or_404(MyUser, id=user_id)
        name = request.POST.get("name")
        surname = request.POST.get("surname")
        email = request.POST.get("email")

        if not any([name, surname, email]):
             return {"error": "All fields are empty!", "user": user}

        if name: user.name = name
        if surname: user.surname = surname
        if email: user.email = email
        
        user.save()
        return {"success": "User updated correctly."}
    except Exception as e:
        if "Http404" in str(type(e)):
             return {"error": f"User with id {user_id} not found."}
        return {"error": "An unexpected error occurred."}

def logout(request):
    request.session.flush()
    return redirect("index")
    




