from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth import get_user_model


@admin.register(get_user_model())
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'phone_number', "email", "first_name", "last_name", "language_code", "is_active",
        "is_verify_phone_number", "is_verify_email", "is_staff", "is_superuser", "display_avatar"
    )
    list_filter = (
        "language_code", "is_active", "is_verify_phone_number", "is_verify_email", "is_staff", "is_superuser"
    )
    search_fields = ('id', 'phone_number', "email", "first_name", "last_name",)
    list_editable = ("is_active", "is_verify_phone_number", "is_verify_email", "is_staff", "is_superuser")
    readonly_fields = ("verify_phone_number_date", "verify_email_date", "created_date",'last_login','date_joined')

    fieldsets = (
        ('Main', {'classes': ('collapse',), 'fields': (
            'phone_number', "email", 'first_name', 'last_name', "avatar", "note", "language_code", "search_document",
        )}),

        ('Address', {'classes': ('collapse',), 'fields': (
            'addresses', 'default_shipping_address', 'default_billing_address',
        )}),

        ('Permission', {'classes': ('collapse',), 'fields': (
            'is_staff', 'is_active', 'is_superuser', 'is_verify_phone_number', 'is_verify_email'
        )}),

        ('Date', {'classes': ('collapse',), 'fields': (
            'date_joined', 'last_login', 'verify_phone_number_date', 'verify_email_date', 'created_date'
        )}),
    )

    add_fieldsets = fieldsets

    def display_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" />', obj.avatar.url)
        else:
            return 'No Avatar'
