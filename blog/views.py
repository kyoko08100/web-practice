from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User

from .forms import BlogForm
from .models import Image, BlogCategory, Blog, BlogComment


# Create your views here.
def index(request):
    blogs = Blog.objects.all().order_by('-pub_time')
    context = {
        'blogs': blogs,
    }
    return render(request, 'blog_index.html', context)


@login_required(login_url="/login")
def manage_blogs(request):
    blogs = Blog.objects.filter(author=request.user).order_by('-pub_time')
    comments = BlogComment.objects.filter(author=request.user).order_by('-pub_time')
    context = {
        'blogs': blogs,
        'comments': comments,
    }
    return render(request, 'blog_manage.html', context)


@login_required(login_url="/login")
def create_blog(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            # 驗證所有圖片
            images = request.FILES.getlist("images")
            images = _valid_image(images)
            if type(images) == str:
                form.add_error('images', images)
                return render(request, "create_post.html", {"form": form})

            # 所有圖片都通過才存
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            form.save_m2m()  # tags

            for img in images:
                Image.objects.create(content_object=blog, image=img)

        else:
            return render(request, 'create_post.html', {'form': form})

        return redirect("/dashboard")

    else:
        form = BlogForm()

    return render(request, "create_post.html", {"form": form})


@login_required(login_url="/login")
def detail(request, blog_id):
    blog = Blog.objects.get(id=blog_id)
    # 取得所有 tags
    tags = blog.tags.all()
    # 取得所有圖片 (GenericForeignKey)
    images = blog.images.all()
    # 評論
    comments = BlogComment.objects.filter(blog_id=blog_id, parent=None)
    context = {
        "blog": blog,
        "tags": tags,
        "images": images,
        "comments": comments,
    }
    return render(request, "post_detail.html", context)


@login_required(login_url="/login")
def update_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)

        if form.is_valid():
            # 驗證所有圖片
            images = request.FILES.getlist("images")
            images = _valid_image(images)
            if type(images) == str:
                form.add_error('images', images)
                return render(request, "update_post.html", {"form": form})

            form.save()

            # 新增新的圖片
            for img in images:
                Image.objects.create(
                    image=img,
                    content_object=blog
                )

            # 刪除被勾選的舊圖片
            delete_ids = request.POST.get("delete_images", "")
            if delete_ids:
                delete_ids = [i for i in delete_ids[:-1].split(",") if i.isdigit()]
                Image.objects.filter(id__in=delete_ids).delete()

            return redirect("blog:detail", blog.id)

    else:
        # GET：帶舊資料到 form
        form = BlogForm(instance=blog)

    # 把「原本的圖片」一起送到前端
    return render(request, "update_post.html", {
        "form": form,
        "blog": blog,
        "images": blog.images.all(),
    })


@login_required(login_url="/login")
def delete_blog(request, blog_id):
    blog = Blog.objects.get(id=blog_id)
    if request.method == "POST":
        blog.delete()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"error": "掛掉了"}, status=400)


@login_required(login_url="/login")
def create_comments(request, blog_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    print(f"request.POST: {request.POST}")
    print(f"request FILES: {request.FILES}")
    content = request.POST.get("content")
    parent_id = request.POST.get("parent_id")

    parent = None
    if parent_id.isdigit():
        parent = get_object_or_404(BlogComment, id=parent_id)
    blog = get_object_or_404(Blog, id=blog_id)

    if not content:
        return JsonResponse({"error": "留言不能為空"}, status=400)

    images = request.FILES.getlist("images")
    images = _valid_image(images)
    if type(images) == str:
        return JsonResponse({"error": images}, status=400)

    comment = BlogComment.objects.create(
        blog=blog,
        author=request.user,
        content=content,
        parent=parent,
    )

    image_urls = []
    for img in images:
        img_obj = Image.objects.create(content_object=comment, image=img)
        image_urls.append(img_obj.image.url)

    return JsonResponse({
        "message": "success",
        "author": comment.author.username,
        "content": comment.content,
        "pub_time": comment.pub_time.strftime("%Y-%m-%d %H:%M:%S"),
        "images": image_urls,
        "parent_id": parent.id if parent else None,
        "parent_name": parent.author.username if parent else None,
    })


def _valid_image(images):
    """
    圖片驗證，如果圖片沒通過驗證就回傳None，有通過就回傳圖片
    :param images:
    :return:
    """
    for img in images:
        if not img.content_type.startswith("image/"):
            return f"{img.name} 不是圖片"
        if img.size > 5 * 1024 * 1024:
            return f"{img.name} 太大 (最大 5MB)"
    return images
