from django.contrib import admin
from django.urls import path, include
from . import views
from .views import portfolio, all_work, graphics_portfolio, about_us, contact_us

urlpatterns = [
    path('', views.portfolio, name='portfolio'),
    path('portfolio/', views.all_work, name='all_work'),
    path('graphics_portfolio/', views.graphics_portfolio, name='graphics_portfolio'),
    path('about_us/', views.about_us, name='about_us'),
    path('contact_us/', views.contact_us, name='contact_us'),
]