# Create your views here.

from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm
from .services.auth_service import login_user, register_user

def index(request):
    context = {
        'app_name': 'Utente',
    }
    if not context:
        return None
    return render(request, 'home.html', context)


def login(request):
    try:
        if request.method == "POST":
            form = LoginForm(request.POST)
            if form.is_valid():
                user = login_user(
                    form.cleaned_data["email"],
                    form.cleaned_data["password"]
                )
                if user:
                    request.session["id_user"] = user["id"]
                    return redirect("dashboard")
                else:
                    return render(request, "login.html", {"form": form, "error": "Credenziali errate"})
        else:
            form = LoginForm()

        return render(request, "login.html", {"form": form})
    except Exception as e :
        print("error: ",e)
        return e


def register(request):
    try:
        if request.method == "POST":
            form = RegisterForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                surname = form.cleaned_data['surname']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                try:
                    if register_user(name, surname, email, password):
                        return redirect('login')
                    else:
                        return render(request, "register.html", {"form": form, "error": "Errore durante la registrazione"})
                except Exception as e:
                    print(e)
                    return render(request, "register.html", {"form": form, "error": "Errore durante la registrazione"})
        else:
            form = RegisterForm()
        context = {
            'app_name': 'Utente',
            'form': form,
        }
        return render(request, 'register.html', context)
    except Exception as e:
        print("Error: ",e)
        return e

