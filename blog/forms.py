from django import forms
from django.forms.widgets import ClearableFileInput

from .models import Blog, BlogCategory, BlogComment


class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True


class BlogForm(forms.ModelForm):

    class Meta:
        model = Blog
        fields = ["title", "content", "category", "tags"]
        widgets = {
            "title": forms.TextInput(attrs={'class': 'form-control', 'placeholder': '請輸入貼文標題'}),
            "content": forms.Textarea(attrs={'class': 'form-control', "placeholder": "在這裡寫下你的想法..."}),
            "category": forms.Select(attrs={'class': 'form-control'}),
            "tags": forms.TextInput(attrs={'class': 'tag-input', 'placeholder': "輸入標籤後按 Enter", "onkeydown": "handleTagInput(event)"}),
        }


# class CommentForm(forms.ModelForm):
#
#     class Meta:
#         model = BlogComment
#         fields = ["content"]
#         widgets = {
#             "content": forms.Textarea(attrs={'class': 'comment-input', "placeholder": "寫下你的留言...", "required": "required"}),
#         }
