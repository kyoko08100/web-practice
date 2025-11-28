import aiohttp
import redis.asyncio as redis
import json
import hashlib

class APIClient:
    def __init__(self):
        self.redis = redis.from_url("redis://localhost:6379")

    def make_key(self, url, method, params, data):
        raw = json.dumps({
            "url": url,
            "method": method,
            "params": params,
            "data": data,
        }, sort_keys=True)
        return "api_cache:" + hashlib.sha256(raw.encode()).hexdigest()

    async def request(self, url, method="POST", params=None, data=None, headers=None, use_cache=True, ttl=3600, **kwargs):
        key = self.make_key(url, method, params, data)

        # 1. 先查 Redis
        # if use_cache and self.redis and (cached := await self.redis.get(key)):
        #     return cached
        # if use_cache:
        #     cached = await self.redis.get(key)
        #     if cached:
        #         return json.loads(cached)
        print(f"method1:{method}")
        print(f"url1:{url}")
        print(f"params1:{params}")
        print(f"data1:{data}")
        print(f"headers1:{headers}")
        print(f"kwargs1:{kwargs}")
        # 2. 若沒有，就打 API
        # headers = {
        #   "Content-Type": "application/json",
        #   "Accept": "application/json",
        # }
        async with aiohttp.ClientSession() as session:
            async with session.request(
                    method,
                    url,
                    params=params,
                    data=data,
                    headers=headers,
                    **kwargs,
            ) as response:
                # print(session._default_headers)
                data = await response.json()
                print(f"data1:{data}")

            # 3. 把結果存回 Redis
            # if use_cache:
            #     await self.redis.set(key, json.dumps(data), ex=ttl)

        return data

    async def gacha_record(self, player_id, record_id, banner, server, lang):
        url = "https://gmserver-api.aki-game2.net/gacha/record/query"
        params = {
            "playerId": player_id,
            "languageCode": lang.value,
            "cardPoolType": int(banner),
            "recordId": record_id,
            "serverId": server.value,
            "cardPoolId": "",
        }
        resp = await self.request(url, method="POST", json=params)
        return [record for record in resp["data"]]
