from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from .views import LoggedGreetingViewSet

router = DefaultRouter()
router.register(r'myapp', LoggedGreetingViewSet)

app_name = 'api'

urlpatterns = [
    url(r'', include(router.urls)),
]
