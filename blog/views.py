from django.shortcuts import render, redirect
from .models import Blog_Post


# Blog Page
def blog(request):
    blog_posts = Blog_Post.objects.filter(is_published=True).order_by('-date_time', '-id')
    return render(request, 'blog/blog_page.html', {'blog_posts': blog_posts})


# Blog Post
def blog_post(request, slug):
    blog_post = Blog_Post.objects.filter(slug=slug, is_published=True).first()
    if blog_post:
        # increment view count
        blog_post.view_count = (blog_post.view_count or 0) + 1
        blog_post.save(update_fields=['view_count'])
        related = Blog_Post.objects.filter(
            is_published=True,
        ).exclude(pk=blog_post.pk).order_by('-date_time', '-id')[:6]
        return render(
            request,
            'blog/blog_post.html',
            {
                'blog_post': blog_post,
                'blog_posts': related,
            },
        )
    else:
        return redirect('blog')