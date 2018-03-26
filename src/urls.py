from rest_framework.routers import DefaultRouter
from django.contrib import admin

from django.conf import settings
from django.urls import path, re_path, include

from django.conf.urls.static import static

router = DefaultRouter()

app_patterns = [
    path('greetings/', include('myapp.urls')),

    path('api/v1/', include('myapp.api')),
    path('mock/v1/', include('myapp.mock')),

    path('admin/', admin.site.urls),
]

app_patterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.SITE_PATH:
    urlpatterns = [
        path(
            '%s/' % settings.SITE_PATH.strip('/'),
            include(app_patterns)
        ),
    ]
else:
    urlpatterns = app_patterns

if settings.DEBUG:
    import debug_toolbar

    if settings.SITE_PATH and settings.SITE_PATH.strip('/'):
        urlpatterns = [
            re_path(r'^%s/__debug__/' % settings.SITE_PATH.strip('/'), include(debug_toolbar.urls)),
        ] + urlpatterns
    else:
        urlpatterns = [
            re_path(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
