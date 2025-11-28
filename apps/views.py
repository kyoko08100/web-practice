import asyncio
import json
import re
import kuro
from kuro.types import WuWaBanner, WuWaServer, Lang
from .utils.kuro_api import APIClient
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
    return redirect('/login')

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

    # 如果使用者傳 JSON，就用它
    if log_file.content_type == "application/json":
        try:
            # decode → 轉成字串 → 解析 JSON
            text = log_file.read().decode("utf-8")
            result = json.loads(text)
            gacha_data = [{"name": r["name"], "rarity": r.get("qualityLevel"), "time": r.get("time")} for r in
                          result["data"]]
        except Exception:
            return JsonResponse({"error": "錯誤的json檔案內容"})

        # 計算已墊抽數
        count = 1
        gacha_list = []
        for r in reversed(result["data"]):
            gacha_list.append(count)
            if r.get("qualityLevel") == 5:
                count = 0
            count += 1
        gacha_list.reverse()
        return JsonResponse({"result": gacha_data, "gachaList": gacha_list}, safe=False,
                            json_dumps_params={"ensure_ascii": False})
    else:
        # 從log檔找到最新的API請求參數
        lines = log_file.read().decode('utf-8').splitlines()
        target = "https://aki-gm-resources-oversea.aki-game.net/aki/gacha/index.html#"
        pattern = re.compile(r'https?://[^\s]+')
        url = ""
        gacha_list = []

        for line in reversed(lines):
            if target in line:
                print("找到：", line.strip())
                urls = pattern.findall(line)[0]
                url = urls.split("\"")[0]
                print(f"url: {url}")
                break

        gacha_data = ""
        if url != "":
            url_split = url.split('?')
            host, params = url_split[0], url_split[1]
            data = {}
            for param in params.split('&'):
                key, value = param.split('=')
                data[key] = value
            client = APIClient()
            result = await client.gacha_record(data['player_id'], data['record_id'], WuWaBanner.FEATURED_RESONATOR, WuWaServer.ASIA, Lang.CHINESE_TRADITIONAL)
            # 沒有返回資料
            if not result:
                return JsonResponse({"error": "沒有找到參數或請求token已過期，請開啟遊戲中的喚取介面後，再將Client.log上傳"})
            gacha_data = [{"name": r.get("name"), "rarity": r.get("qualityLevel"), "time": r.get("time")} for r in result]
            # 計算已墊抽數
            count = 0
            gacha_list = []
            for r in result:
                if r.get("qualityLevel") == 5:
                    gacha_list.append(count)
                    count = 1
                else:
                    count += 1
        return JsonResponse({"result": gacha_data, "gachaList": gacha_list}, safe=False, json_dumps_params={"ensure_ascii": False})
