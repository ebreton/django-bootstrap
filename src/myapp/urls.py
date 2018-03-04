from django.urls import path

from myapp import views

app_name = 'crud'

urlpatterns = [
    path('', views.GreetingList.as_view(), name='greeting-list', ),
    path('new/', views.GreetingCreate.as_view(), name='greeting-create'),
    path('(?P<pk>\d+)/', views.GreetingDetail.as_view(), name='greeting-detail'),
    path('(?P<pk>\d+)/update/', views.GreetingUpdate.as_view(), name='greeting-update'),
    path('(?P<pk>\d+)/delete/', views.GreetingDelete.as_view(), name='greeting-delete'),

    path('version/', views.version),
    path('version/(?P<label>\w+)/', views.version, name='myapp-version'),
]
