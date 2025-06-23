from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Contact, NewsLetter
# Register your models here.


class ContactAdmin(ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('created_at',)


class NewsLetterAdmin(ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)
    list_filter = ('created_at',)


admin.site.register(Contact, ContactAdmin)
admin.site.register(NewsLetter, NewsLetterAdmin)
