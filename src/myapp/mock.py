from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from .views import MockGreetingViewSet

router = DefaultRouter()
router.register(r'myapp', MockGreetingViewSet)

app_name = 'mock'

urlpatterns = [
    url(r'', include(router.urls)),
]
