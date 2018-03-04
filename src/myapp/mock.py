from rest_framework.routers import DefaultRouter

from .views import MockGreetingViewSet

app_name = 'mock'

router = DefaultRouter()
router.register('greetings', MockGreetingViewSet)

urlpatterns = router.urls
