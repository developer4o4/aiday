# admin.py
from django.contrib import admin
from .models import Qrcode, User

@admin.register(Qrcode)
class QrcodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'created_at', 'is_used']
    list_filter = ['is_used', 'created_at']
    search_fields = ['code']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'direction', 'qr_code', 'created_at']
    list_filter = ['direction', 'region', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    readonly_fields = ['qr_code', 'created_at'] 