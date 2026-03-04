from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from user.models import MyUser
from document.views import document_index
# Create your views here.


def user_index(request):
    user_id = request.session.get("id_user")
    if not user_id:
        return redirect("home")

    context = {
        "appname": "User",
        "id_user": user_id,
        "user": get_user(request)
    }

    try:
        if request.method == "POST":
            azione = request.POST.get("azione")

            if azione == "logout":
                return logout(request)

            if azione in ["create_document", "update_document", "delete_document"]:
                extra = document_index(request)
                if extra:
                    context.update(extra)
                return redirect("dashboard")

            if azione == "update_user":
                extra = update_user(request)
                if extra:
                    context.update(extra)
                return redirect("dashboard")

        doc_context = document_index(request)
        if doc_context:
            context.update(doc_context)

    except Exception as e:
        print("Errore in user_index:", e)
        context["error"] = "An unexpected error occurred."

    return render(request, "user/homepage.html", context)


def get_user(request):
    user_id = request.session.get("id_user")
    if not user_id:
        return None
    
    try:
        return MyUser.objects.filter(id=user_id).first()
    except Exception as e:
        print("Errore nel recupero utente:", e)
        return None


def logout(request):
    request.session.flush()
    return redirect("home")


def update_user(request):
    user_id = request.session.get("id_user")
    
    if not user_id:
        return {"error": "User not logged in."}
    
    try:
        user = get_object_or_404(MyUser, id=user_id)

        name = request.POST.get("name", "").strip()
        surname = request.POST.get("surname", "").strip()
        email = request.POST.get("email", "").strip()

        if not any([name, surname, email]):
            return {
                "error": "All fields are empty!",
                "user": user
            }

        if name:
            user.name = name
        if surname:
            user.surname = surname
        if email:
            user.email = email
        
        user.save()

        return {
            "success": "User updated correctly.",
            "user": user
        }
    
    except Http404:
        return {"error": f"User with id {user_id} not found."}
    except Exception as e:
        print("Errore in update_user:", e)
        return {"error": "An unexpected error occurred."}
    




