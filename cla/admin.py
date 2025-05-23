from django.contrib import admin
from .models import UserType

class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_librarian')

admin.site.register(UserType, UserTypeAdmin)

