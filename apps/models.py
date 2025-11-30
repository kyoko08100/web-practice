from django.db import models
from django.utils import timezone
import datetime

# Create your models here.
# app/models.py

class Captcha(models.Model):
    email = models.EmailField(null=False)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return self.created_at + datetime.timedelta(minutes=10) < timezone.now()
