from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


def index(request):
    return redirect('/login')

def login_view(request):
    if request.method == "POST":
        user = authenticate(username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            login(request, user)
            return redirect("/dashboard")
        else:
            return HttpResponse("Invalid login details supplied.")
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return render(request, "login.html")

@login_required(login_url="/login")
def dashboard(request):
    return render(request, "dashboard.html")

@login_required
def restaurant_finder(request):
    context = {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'restaurant_finder.html', context)

@login_required
def gacha_simulator(request):
    return render(request, 'genshin_gacha.html')