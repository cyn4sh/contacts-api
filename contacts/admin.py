from django.contrib import admin
from contacts.models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "name", "phone", "email", "address", "created_at", "updated_at")
    search_fields = ("name", "phone", "email", "address")
    list_filter = ("created_at", "updated_at")