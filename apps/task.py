from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email(captcha, email):
    print("寄出郵件")
    send_mail(
        "你的驗證碼",
        f"你的驗證碼是：{captcha}，10 分鐘內有效。",
        None,  # 使用 DEFAULT_FROM_EMAIL
        [email],
    )