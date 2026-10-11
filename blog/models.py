from django.db import models
import datetime
from django.utils import timezone
from django.utils.text import slugify
from autoslug import AutoSlugField
from unidecode import unidecode
from ckeditor.fields import RichTextField


#unicode slug
def custom_slugify(value):
    # First, transliterate the text to the closest ASCII representation using unidecode
    value = unidecode(value)
    # Then, use Django's built-in slugify function to generate the slug
    return slugify(value)

#Blog_post
class Blog_Post(models.Model):
    category= models.CharField(max_length=900)
    title= models.CharField(max_length=900)
    author= models.CharField(max_length=900)
    about_author= models.CharField(max_length=900, blank=True, null=True)
    author_profile_link= models.CharField(max_length=900, blank=True, null=True)
    slug = AutoSlugField(populate_from='title', unique=True, blank=True, slugify=custom_slugify, always_update=True)
    content= RichTextField(blank=True, null=True)
    meta_description= models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='upload/blog_image',blank=True,default=None)
    date_time = models.DateTimeField(auto_now_add=timezone.now())
    is_published = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date_time', '-id']

    def save(self , *args , **kwargs):
        self.slug = slugify(self.title)
        super(Blog_Post ,self).save(*args , **kwargs)


    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self):
        return f'/blog/blog_post/{self.slug}/'
