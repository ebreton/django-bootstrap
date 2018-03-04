from rest_framework.routers import DefaultRouter
from django.contrib import admin

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

router = DefaultRouter()

app_patterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('myapp.urls')),

    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/', include('myapp.api')),
    url(r'^mock/v1/', include('myapp.mock')),
]

app_patterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.SITE_PATH:
    urlpatterns = [
        url(
            r'^%s/' % settings.SITE_PATH.strip('/'),
            include(app_patterns)
        ),
    ]
else:
    urlpatterns = app_patterns
