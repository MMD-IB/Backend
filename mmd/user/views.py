from django.shortcuts import render,get_object_or_404
from user.models import MyUser
# Create your views here.


def user_index(request):
    if "id_user" not in request.session or request.session["id_user"] is None:
        return render(request,"home.html")
    context = {
        "appname":"User",
        "id_user": request.session["id_user"],
        "user": get_user(request)
    }
    if request.method == "POST":
        azione = request.POST.get("azione")             
        if azione == "logout":
            return logout(request)
    if request.method == "PUT":
        extra = update_user(request)
        context.update(extra)
    return render(request,"user-index.html",context)


def get_user(request):
    user_id = request.session["id_user"]
    return MyUser.objects.filter(id=user_id).first()


def logout(request):
    request.session["id_user"] = None
    return render(request,"home.html", {"appname":"Logout"})


def update_user(request):
    user_id = request.session["id_user"]
    user = get_object_or_404(MyUser, id=user_id)

    name = request.POST.get("name")
    surname = request.POST.get("surname")
    email = request.POST.get("email")

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
        "success": "User updated correctly",
        "user": user
    }
    




