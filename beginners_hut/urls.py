
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns # new
from django.views.static import serve

from django.conf import settings
from django.conf.urls.static import static

# sitemaps 
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import *
from portfolio.sitemaps import *
from django.views.generic import TemplateView

sitemaps={
    'portfolio': StaticPortfolioSitemap,
    'blog': StaticBlogSitemap,
    'blog_post': BlogSitemap,
}


from django.conf.urls import handler404
from django.shortcuts import render


def custom_page_not_found(request, exception):
    return render(request, '404.html', status=404)

urlpatterns = [

    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),#new
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),#new

    path('sitemap.xml/', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap' ),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('super_admin/', admin.site.urls),
    path ('',include('portfolio.urls')),
    path ('admin/',include(('admin_panel.urls', 'admin_panel'), namespace='admin_panel')),
    path ('blog/',include('blog.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
