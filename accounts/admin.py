from django.contrib import admin
from .models import User
from unfold.admin import ModelAdmin
# Register your models here.


class UserAdmin(ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')


admin.site.register(User, UserAdmin)
