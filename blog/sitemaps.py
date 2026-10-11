from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Blog_Post


class StaticBlogSitemap(Sitemap):
    def items(self):
        return['blog']

    def location (self, item):
        return reverse(item)

class BlogSitemap(Sitemap):
    def items(self):
        return Blog_Post.objects.all()
