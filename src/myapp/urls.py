from django.conf.urls import url
from myapp import views

urlpatterns = [
    url(r'^$', views.home, name='myapp-home'),
    url(r'^version/$', views.version),
    url(r'^version/(?P<label>\w+)/$', views.version, name='myapp-version'),
]
