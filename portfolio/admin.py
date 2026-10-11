from django.contrib import admin

# Register your models here.
from .models import Website_Portfolio, Testimonial, Print_Design, Post_Design

admin.site.register(Website_Portfolio)
admin.site.register(Testimonial)
admin.site.register(Print_Design)
admin.site.register(Post_Design)
