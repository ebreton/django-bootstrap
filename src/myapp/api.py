from rest_framework.routers import DefaultRouter

from .views import LoggedGreetingViewSet

app_name = 'api'

router = DefaultRouter()
router.register('greetings', LoggedGreetingViewSet)

urlpatterns = router.urls
