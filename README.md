# Django 網頁練習專案

這是一個簡單的 Django 專案，用來做一些想做的功能跟學習Django框架。

## ✨ 已開發功能

* 基本登入、登出、註冊帳號功能: 透過Celery+Redis實現非同步寄送驗證碼
* 附近餐廳查詢: 透過Google map API 查詢附近餐廳
* 抽卡模擬器: 透過模擬抽卡試試運氣
* 鳴潮抽卡紀錄查詢: 透過 API 取得與資料整理
* 簡易社群網站: 新增、管理貼文、貼文留言。使用signal實現刪除含圖片之貼文、留言時同時刪除後台圖片檔

## 📦 環境需求

* Python 3.10+
* Django 5.2
* 使用 uv 管理虛擬環境

## 🚀 專案安裝與啟動

### 1. 建立並啟動虛擬環境

```bash
uv venv
source .venv/bin/activate   # Windows 使用: .venv\\Scripts\\activate
```

### 2. 安裝相依套件

```bash
uv sync
```

### 3. 套用資料庫遷移

```bash
python manage.py migrate
```

### 4. 啟動開發伺服器

```bash
python manage.py runserver
```

伺服器預設運行於： [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## 📁 專案結構（示例）

```
mysite/
├── mysite/           # 主設定檔（settings.py, urls.py 等）
├── app/              # 主要應用程式
├── templates/        # HTML 模板
├── static/           # 靜態檔案（JS, CSS, Images）
└── manage.py
```

## ⚙️ 常用指令

* 建立新 App： `python manage.py startapp appname`
* 建立超級使用者： `python manage.py createsuperuser`
* 更新model： `python manage.py makemigrations`、`python manage.py migrate`

## 📝 備註
.env參數
```dotenv
SECRET_KEY='your_django_SECRET_KEY'
GOOGLE_MAPS_API_KEY='your_GOOGLE_MAPS_API_KEY'
EMAIL_HOST="your_EMAIL_HOST"
EMAIL_HOST_USER="your_EMAIL_HOST_USER"
EMAIL_HOST_PASSWORD="your_EMAIL_HOST_PASSWORD"
CELERY_BROKER_URL="your_CELERY_BROKER_URL"
CELERY_RESULT_BACKEND="your_CELERY_RESULT_BACKEND"
DEBUG=True
```
---

