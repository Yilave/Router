from django.urls import path
from . import views


urlpatterns = [
     path('', views.index, name="index"),
     path('get_route_api/', views.get_route_api, name='get_route_api'),
]
