import os
from django.shortcuts import render, get_object_or_404
from .services.query import (
    create_document,
    create_document_noSQL,
    get_documents_by_user,
    get_document_by_id,
    update_document_status,
    delete_document
)

def document_index(request):
    if "id_user" not in request.session or request.session["id_user"] is None:
        return {"error": "User not logged in."}


    user_id = request.session.get("id_user")
    if not user_id:
        return None

    search_query = request.GET.get("q")
    context = {
        "id_user": user_id,
        "documents": get_documents_by_user(user_id, query=search_query)
    }

    try:
        if request.method == "POST":
            azione = request.POST.get("azione")

            if azione == "create_document":
                title = request.POST.get("title")
                file = request.FILES["file_upload"]
                
                # Extract metadata
                file_name = file.name
                file_type = os.path.splitext(file_name)[1]
                file_size = f"{file.size / 1024:.2f} KB"
                
                contenuto = file.read().decode("utf-8")
                
                extra = create_document(
                    title=title,
                    id_user=user_id,
                    file_name=file_name,
                    file_type=file_type,
                    file_size=file_size
                )
                context.update(extra)

                if extra.get("success"):
                    document_id = extra.get("document_id")
                    create_document_noSQL(document_id, contenuto)

                context["documents"] = get_documents_by_user(user_id)

            elif azione == "update_document":
                document_id = request.POST.get("document_id")
                status = request.POST.get("status")
                extra = update_document_status(document_id, status, user_id)
                context.update(extra)

                context["documents"] = get_documents_by_user(user_id)

            elif azione == "delete_document":
                document_id = request.POST.get("document_id")
                extra = delete_document(document_id, user_id)
                context.update(extra)

                context["documents"] = get_documents_by_user(user_id)

    except Exception as e:
        print("error: ", e)
        context["error"] = str(e)
        context["documents"] = get_documents_by_user(user_id)

    return context

