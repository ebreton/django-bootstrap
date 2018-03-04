from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.options import ModelAdmin
from django.conf import settings

from log_utils import LoggedModelAdminMixin
from .models import User, Greeting


admin.autodiscover()
admin.site.site_url = settings.SITE_PATH
admin.site.site_header = "MyAPP Admin"
admin.site.site_title = "myapp"


class EPFLUserModelAdmin(UserAdmin):
    list_display = ('username', 'email', 'last_login', 'is_superuser')


class GreetingLoggedModelAdmin(LoggedModelAdminMixin, ModelAdmin):
    pass


admin.site.register(User, EPFLUserModelAdmin)
admin.site.register(Greeting, GreetingLoggedModelAdmin)
