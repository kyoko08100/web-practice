import asyncio
import json
import random
import re
import kuro
from kuro.types import WuWaBanner, WuWaServer, Lang

from .forms import RegisterForm
from .utils.kuro_api import APIClient
import aiohttp
import requests
import datetime

import apps.utils.api.kuro_function as my_kuro

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from .models import Captcha
from .task import send_email
from .utils.achievement import get_achievements


def index(request):
    return redirect('/dashboard')


def login_view(request):
    if request.method == "GET":
        if request.session.get('_auth_user_id'):
            return redirect('/dashboard')
    if request.method == "POST":
        user = authenticate(username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            login(request, user)
            return redirect("/dashboard")
        else:
            messages.error(request, "帳號或密碼錯誤")
            return render(request, "login.html")
    return render(request, "login.html")


def register(request):
    if request.method == "GET":
        form = RegisterForm()
        return render(request, "register.html", {"form": form})
    elif request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():
            # captcha標記為已使用
            captcha_obj = form.cleaned_data["captcha"]
            captcha_obj.is_used = True
            captcha_obj.save()

            # 建立帳號
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "註冊成功！請登入")
            return redirect("/login")
        else:
            return render(request, "register.html", {"form": form})
    else:
        return render(request, "register.html")


def send_captcha(request):
    email = request.POST.get("email")
    if not email:
        return JsonResponse({"error": "請輸入email!"}, status=400)

    user = User.objects.filter(email=email).first()
    if user:
        return JsonResponse({"error": "該email已被註冊!"}, status=400)

    newest_captcha = Captcha.objects.filter(email=email).last()
    if newest_captcha and timezone.now() < newest_captcha.created_at + datetime.timedelta(seconds=60):
        return JsonResponse({"error": "60秒後才能取得新的驗證碼!"}, status=429)

    # 隨機 6 位數
    code = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    captcha = ""
    for i in range(6):
        c = random.randint(0, len(code) - 1)
        captcha += code[c]

    # 寄出郵件
    send_email(captcha, email)

    # 儲存
    Captcha.objects.create(email=email, code=captcha)

    return JsonResponse({"message": "驗證碼已寄出"})


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


def dashboard(request):
    return render(request, "dashboard.html")


@login_required(login_url="/login")
def restaurant_finder(request):
    context = {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'restaurant_finder.html', context)


def gacha_simulator(request):
    return render(request, 'gacha.html')


def gacha_history(request):
    if request.method == "GET":
        return render(request, 'gacha_history_viewer.html')
    return render(request, 'gacha_history_viewer.html')


async def get_gacha_history(request):
    log_file = request.FILES.get("log_file")
    pool_type = request.POST.get("pool_type")

    try:
        pool_type = int(pool_type)
    except Exception:
        return JsonResponse({"error": "錯誤的卡池"})
    if pool_type < 1 or pool_type > 9:
        return JsonResponse({"error": "錯誤的卡池"})

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
            result = await client.gacha_record(data['player_id'], data['record_id'], WuWaBanner(pool_type),
                                               WuWaServer.ASIA, Lang.CHINESE_TRADITIONAL)

            # 沒有返回資料
            if not result:
                if isinstance(result, list) and len(result) == 0:
                    return JsonResponse(
                        {"error": "暫無資料"})
                return JsonResponse(
                    {"error": "沒有找到參數或請求token已過期，請開啟遊戲中的喚取介面後，再將Client.log上傳"})
            gacha_data = [{"name": r.get("name"), "rarity": r.get("qualityLevel"), "time": r.get("time")} for r in
                          result]
            # 計算已墊抽數
            count = 1
            gacha_list = []
            for data in reversed(gacha_data):
                if data.get("rarity") == 5:
                    gacha_list.append(count)
                    count = 0
                count += 1
            gacha_list.append(count - 1)  # 最後還沒出五星的抽數
        return JsonResponse({"result": gacha_data, "gachaList": gacha_list[::-1]}, safe=False,
                            json_dumps_params={"ensure_ascii": False})


def achievement_record(request):
    achievements = json.load(open('achievements.json', 'r'))
    achievements_state = json.load(open('achievements_state.json', 'r'))
    if not achievements:
        achievements = get_achievements()
    # json_file = open('achievements_state.json', 'r')
    # d = json.load(json_file)
    # new_a = []
    # for n1, four in enumerate(d):
    #     for n2, (key, value) in enumerate(four.items()):
    #         for n3, (k, v) in enumerate(value.items()):
    #             for n4, aci in enumerate(v):
    #                 new_d = {
    #                     "name": f"{n1}a{n3}a{n4}",
    #                     "completed": False
    #                 }
    #                 new_a.append(new_d)
    # with open("achievements_state.json", "w", encoding="utf-8") as f:
    #     json.dump(new_a, f, ensure_ascii=False, indent=2)
    context = {
        'achievements': json.dumps(achievements, ensure_ascii=False),
        'achievements_state': json.dumps(achievements_state, ensure_ascii=False),
    }
    return render(request, "achievement_record.html", context)


def update_achievements(request):
    get_achievements()
    achievements = json.load(open('achievements.json', 'r'))
    return JsonResponse({"achievements": json.dumps(achievements, ensure_ascii=False)}, safe=False,
                        json_dumps_params={"ensure_ascii": False})
