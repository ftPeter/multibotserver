from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('refresh', views.refresh_robot_data, name='refresh'),
    path('<int:pk>/uploadimage', views.upload_image, name='upload_image'),
    path('<int:pk>/<str:action>', views.perform_action, name='perform_action'),
    path('gallery/<int:pk>', views.show_indiv_gallery, name='indiv_gallery'),
    path('gallery', views.show_gallery, name='gallery')
]