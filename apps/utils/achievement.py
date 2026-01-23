import json
import requests
from bs4 import BeautifulSoup
from opencc import OpenCC


def get_data():
    url = "http://api.kurobbs.com/wiki/core/catalogue/item/getEntryDetail"
    header = {
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "wiki_type": "9",
    }

    data = {
        "id": 1220879855033786368,
    }
    response = requests.post(url, data=data, headers=header)
    content = response.json().get("data").get("content").get("modules")[0].get("components")[0].get("content")
    return content


def get_achievements():
    raw_data = json.load(open('achievements.json', 'r'))
    html = get_data()
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    categories = soup.find_all("summary")
    data = []
    name_list = ["名稱", "版本", "合集", "描述", "獎勵"]
    a_type = ""  # 成就合集(類別) ex. 往日之音 今州 Ⅱ
    cc = OpenCC('s2tw')  # s2tw: 簡體轉臺灣正體
    for s, (cate, table) in enumerate(zip(categories, tables)):
        a_dict = {}
        count = 0
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            a = {}
            for i, td in enumerate(tds):  # i對應name_list
                text = cc.convert(td.text.strip())
                if i >= 5:
                    continue
                if i == 2:
                    if a_type != text:
                        count = 0
                    a_type = text
                else:
                    a[name_list[i]] = text
            if a_dict.get(a_type):
                a["連結"] = raw_data[s].get(cc.convert(cate.text.strip())).get(a_type)[count].get("連結")
                a_dict.get(a_type).append(a)
            else:
                if a_type != "合集":
                    a["連結"] = raw_data[s].get(cc.convert(cate.text.strip())).get(a_type)[count].get("連結")
                    a_dict[a_type] = [a]
            count += 1
        data.append({cc.convert(cate.text.strip()): a_dict})
    with open("achievements.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data
