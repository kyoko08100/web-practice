from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from taggit.managers import TaggableManager

# Create your models here.

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_time = models.DateTimeField(auto_now_add=True)
    # 可以反查自己所有圖片
    images = GenericRelation("Image")
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = TaggableManager(blank=True)

    def get_images(self):
        ct = ContentType.objects.get_for_model(Blog)
        return Image.objects.filter(content_type=ct, object_id=self.id)

class Image(models.Model):
    image = models.ImageField(upload_to="static/blog")
    # GenericForeignKey 三要素
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    uploaded_at = models.DateTimeField(auto_now_add=True)

class BlogComment(models.Model):
    content = models.TextField()
    pub_time = models.DateTimeField(auto_now_add=True)
    # 可以反查自己所有圖片
    images = GenericRelation("Image")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 子留言
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="replies",  # 可從 parent.replies.all() 取得所有子留言
        on_delete=models.CASCADE,
    )

    def get_images(self):
        ct = ContentType.objects.get_for_model(BlogComment)
        return Image.objects.filter(content_type=ct, object_id=self.id)

    def children(self):
        return BlogComment.objects.filter(parent=self)