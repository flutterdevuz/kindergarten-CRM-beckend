from django.urls import path
from .views import (
    GroupListAPIView, GroupCreateAPIView, GroupRetrieveAPIView,
    GroupUpdateAPIView, GroupDeleteAPIView,
    CameraListAPIView, CameraCreateAPIView, CameraRetrieveAPIView,
    CameraUpdateAPIView, CameraDeleteAPIView
)

app_name = 'groups'

urlpatterns = [
    # Group URLs
    path('kindergarden/groups/', GroupListAPIView.as_view(), name='group_list'),
    path('kindergarden/groups/add/', GroupCreateAPIView.as_view(), name='group_add'),
    path('kindergarden/groups/<str:pk>/', GroupRetrieveAPIView.as_view(), name='group_detail'),
    path('kindergarden/groups/<str:pk>/edit/', GroupUpdateAPIView.as_view(), name='group_edit'),
    path('kindergarden/groups/<str:pk>/delete/', GroupDeleteAPIView.as_view(), name='group_delete'),

    # Camera URLs
    path('kindergarden/camera/', CameraListAPIView.as_view(), name='camera_list'),
    path('kindergarden/camera/add/', CameraCreateAPIView.as_view(), name='camera_add'),
    path('kindergarden/camera/<str:pk>/', CameraRetrieveAPIView.as_view(), name='camera_detail'),
    path('kindergarden/camera/<str:pk>/edit/', CameraUpdateAPIView.as_view(), name='camera_edit'),
    path('kindergarden/camera/<str:pk>/delete/', CameraDeleteAPIView.as_view(), name='camera_delete'),
]
