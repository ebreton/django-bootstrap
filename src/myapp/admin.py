from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.conf import settings

from .models import User


admin.autodiscover()
admin.site.site_url = settings.SITE_PATH
admin.site.site_header = "MyAPP Admin"
admin.site.site_title = "myapp"


class EPFLUserModelAdmin(UserAdmin):
    list_display = ('username', 'email', 'last_login', 'is_superuser')


admin.site.register(User, EPFLUserModelAdmin)
