import aiohttp
import inspect
import json
from aiohttp import ClientTimeout, ContentTypeError
from typing import Any, Dict, List, Union, Literal, Mapping, Optional
import kuro
from aiohttp import request
from kuro.types import Region
from kuro.utility import auth
from kuro import constants, types
import requests

async def login(email: str, password: str):
    client = kuro.Client()
    login_result = await client.game_login(email, password)
    my_token = await client.get_game_token(login_result.code)
    oauth_code = await client.generate_oauth_code(my_token.access_token)
    player_info = await client.get_player_info(oauth_code)
    game_user = await client.get_game_user(player_info.get('Asia').uid, my_token.access_token, Region.OVERSEAS, login_result.username)
    player_role = await client.get_player_role(oauth_code, player_info.get('Asia').uid, 'Asia')
    # base_data = await get_base_data(player_info.get('Asia').uid)
    # role_list = await get_role_list(oauth_code, auth.generate_uuid_uppercase(), 3)
    login_result = await game_login(email, password)

    print(f"login_result: {login_result}")
    # print(f"my_token: {my_token}")
    # print(f"oauth_code: {oauth_code}")
    print(f"player_info: {player_info}")
    # print(f"player_info: {player_info.get('Asia').uid}")
    # print(f"player_info: {type(player_info.get('Asia'))}")
    # print(f"game_user: {game_user}")
    print(f"player_role: {player_role}")
    # print(f"base_data: {base_data}")
    # print(f"role_list: {role_list}")

async def get_base_data(role_id):
    url = "https://api.kurobbs.com/aki/roleBox/akiBox/baseData"
    header = {
        "source": "ios",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)  KuroGameBox/2.6.3",
    }

    data = {
        "gameId": 3,
        "serverId": "86d52186155b148b5c138ceb41be9650",
        "roleId": role_id,
    }
    response = requests.post(url, json=data, headers=header)
    return response.json()

async def get_role_list(token: str, did: str, game_id: int):
    url = "https://api.kurobbs.com/gamer/role/list"
    header = {
        "source": "ios",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)  KuroGameBox/2.6.3",
    }
    header.update(
        {
            "token": token,
            "devCode": did,
        }
    )
    data = {"gameId": game_id}
    response = requests.post(url, json=data, headers=header)
    return response.json()

async def game_login(email: str, password: str):
    url = "https://sdkapi.kurogame-service.com/sdkcom/v2/login/emailPwd.lg"
    header = {
        "source": "ios",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)  KuroGameBox/2.6.3",
    }
    data = {
        "__e__": 1,
        "email": email,
        "client_id": "7rxmydkibzzsf12om5asjnoo",  # KR_PRODUCT_KEY in kr_sdk_config.json
        "deviceNum": auth.generate_uuid_uppercase(),
        "password": auth.encode_password(password),
        "platform": "PC",
        "productId": "A1730",
        "productKey": "5c063821193f41e09f1c4fdd7567dda3",  # KR_PRODUCT_KEY in kr_sdk_config.json
        "projectId": "G153",
        "redirect_uri": 1,
        "response_type": "code",
        "sdkVersion": "2.6.0h",
        "channelId": "240",
    }
    data["sign"] = auth.encode_md5_parameter(
        data, constants.APP_KEYS[types.Game.WUWA][Region.OVERSEAS]
    )

    response = requests.post(url, json=data, headers=header)
    return response.json()