from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Post, Profile


# Register your models here.
admin.site.register(Post)
admin.site.register(Profile)