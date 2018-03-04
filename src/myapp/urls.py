from django.conf.urls import url, include
from myapp import views

greeting_patterns = [
    url(r'^$', views.GreetingList.as_view(), name='greeting-list', ),
    url(r'^new/$', views.GreetingCreate.as_view(), name='greeting-create'),
    url(r'^(?P<pk>\d+)/$', views.GreetingDetail.as_view(), name='greeting-detail'),
    url(r'^(?P<pk>\d+)/update/$', views.GreetingUpdate.as_view(), name='greeting-update'),
    url(r'^(?P<pk>\d+)/delete/$', views.GreetingDelete.as_view(), name='greeting-delete'),

    url(r'^version/$', views.version),
    url(r'^version/(?P<label>\w+)/$', views.version, name='myapp-version'),
]

crud_patterns = [
    url(r'^greetings/', include(greeting_patterns)),
]

app_name = 'crud'

urlpatterns = [
    url(r'^', include(crud_patterns)),
]
