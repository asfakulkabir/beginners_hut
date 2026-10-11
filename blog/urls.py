
from django.contrib import admin
from django.urls import path, include
from . import views
from .views import blog, blog_post
urlpatterns = [
    path('', views.blog, name='blog'),
    path('blog_post/<str:slug>/' , views.blog_post , name="blog_post"),
]
