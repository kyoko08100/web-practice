import asyncio
import re
import kuro
from kuro.types import WuWaBanner, WuWaServer, Lang
import aiohttp
import requests

import apps.utils.api.kuro_function as my_kuro

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
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

@login_required(login_url="/login")
def kuro_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        asyncio.run(my_kuro.login(email, password))
        return redirect("/dashboard")
    return render(request, "kuro_login.html")

def logout_view(request):
    logout(request)
    return render(request, "login.html")

@login_required(login_url="/login")
def dashboard(request):
    return render(request, "dashboard.html")

@login_required(login_url="/login")
def restaurant_finder(request):
    context = {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'restaurant_finder.html', context)

@login_required(login_url="/login")
def gacha_simulator(request):
    return render(request, 'gacha.html')

@login_required(login_url="/login")
async def gacha_history(request):
    if request.method == "GET":
        return render(request, 'gacha_history_viewer.html')
    return render(request, 'gacha_history_viewer.html')

async def get_gacha_history(request):
    log_file = request.FILES.get("log_file")
    lines = log_file.read().decode('utf-8').splitlines()
    target = "https://aki-gm-resources-oversea.aki-game.net/aki/gacha/index.html#"
    pattern = re.compile(r'https?://[^\s]+')
    url = ""
    gacha_list = []

    for line in reversed(lines):
        # line = line.decode("utf-8", errors="ignore")
        if target in line:
            print("找到：", line.strip())
            urls = pattern.findall(line)[0]
            url = urls.split("\"")[0]
            print(f"url: {url}")
            break

    gacha_data = "沒有找到"
    if url != "":
        url_split = url.split('?')
        host, params = url_split[0], url_split[1]
        data = {}
        for param in params.split('&'):
            key, value = param.split('=')
            data[key] = value
        result = await kuro.Client().get_gacha_record(
            player_id=data['player_id'],
            record_id=data['record_id'],
            banner=WuWaBanner.FEATURED_RESONATOR,
            server=WuWaServer.ASIA,
            lang=Lang.CHINESE_TRADITIONAL
        )
        gacha_data = [{"name": r.name, "rarity": r.rarity, "time": r.time.strftime('%Y-%m-%d %H:%M:%S')} for r in result]
        # 計算已墊抽數
        count = 0
        gacha_list = []
        for r in result:
            if r.rarity == 5:
                gacha_list.append(count)
                count = 1
            else:
                count += 1
    return JsonResponse({"result": gacha_data, "gachaList": gacha_list}, safe=False, json_dumps_params={"ensure_ascii": False})
