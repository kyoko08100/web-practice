from django import forms
from django.contrib.auth.models import User

from .models import Captcha


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=2, error_messages={
        'required': "請輸入使用者名稱!",
        'max_length': "使用者名稱長度在2~20之間!",
        'min_length': "使用者名稱長度在2~20之間!"
    }, widget=forms.TextInput(attrs={"placeholder": "請輸入使用者名稱"}))
    email = forms.EmailField(error_messages={"required": "請輸入電子郵件!", "invalid": "請輸入一個正確的電子郵件!"}, widget=forms.TextInput(attrs={"placeholder": "請輸入電子郵件"}))
    captcha = forms.CharField(max_length=6, min_length=6, widget=forms.TextInput(attrs={"placeholder": "請輸入驗證碼", "style": "flex: 1"}))
    password = forms.CharField(max_length=20, min_length=6, widget=forms.TextInput(attrs={"type": "password", "placeholder": "請輸入密碼"}))
    re_password = forms.CharField(max_length=20, min_length=6, widget=forms.TextInput(attrs={"type": "password"}))

    def clean_email(self):
        email = self.cleaned_data['email']
        user_exists = User.objects.filter(email=email).exists()
        if user_exists:
            raise forms.ValidationError("此電子郵件已被註冊!")
        return email

    def clean_captcha(self):
        captcha = self.cleaned_data['captcha']
        email = self.cleaned_data['email']

        captcha_obj = Captcha.objects.filter(
            email=email, code=captcha, is_used=False
        ).order_by("-created_at").first()

        if not captcha_obj:
            raise forms.ValidationError("驗證碼錯誤!")

        if captcha_obj.is_expired():
            raise forms.ValidationError("驗證碼已過期!")

        return captcha_obj

    def clean_re_password(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        if password != re_password:
            raise forms.ValidationError("密碼和確認密碼不一致!")
        return password
