from django.urls import path
from . import views


app_name = 'blog'
urlpatterns = [
    path('', views.index, name='index'),
    path('manage', views.manage_blogs, name='manage'),
    path('create', views.create_blog, name='create'),
    path('detail/<int:blog_id>', views.detail, name='detail'),
    path('update/<int:blog_id>', views.update_blog, name='update'),
    path('delete/<int:blog_id>', views.delete_blog, name='delete'),
    path('comments/<int:blog_id>', views.create_comments, name='comments'),
]