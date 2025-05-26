from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Order, OrderItem
# Register your models here.


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    tab = True


class OrderAdmin(ModelAdmin):
    list_display = ('full_name', 'id', 'user__first_name', 'status', 'shipping_address', 'phone_number',
                    'email', 'total_amount', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ['id', 'full_name', 'user', 'status',
                     'phone_number']
    inlines = [OrderItemInline]
    actions = ['mark_as_paid', 'mark_as_shipped']


admin.site.register(Order, OrderAdmin)
