from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('refresh', views.refresh_robot_data, name='refresh'),
    path('<str:action>/<int:pk>', views.perform_action, name='perform_action'),
]