from django.shortcuts import render,get_object_or_404
from user.models import MyUser
# Create your views here.


def user_index(request):
    context = {"appname":"User"}
    
    return render(request,"user-index.html",context)

def get_users(request):
    context = {"appname":"Users"}

    users = MyUser.objects.all()
    context["users"] = users
    return render(request,context)