from django.urls import path
from .views import (
    KindergartenLoginView, StaffLoginView, ParentLoginView,
    ParentListAPIView, ParentCreateAPIView, ParentRetrieveAPIView, ParentUpdateAPIView, ParentDeleteAPIView
)

app_name = 'users'

urlpatterns = [
    # Login URLs
    path('kindergarden/login/', KindergartenLoginView.as_view(), name='kindergarden_login'),
    path('staff/login/', StaffLoginView.as_view(), name='staff_login'),
    path('parents/login/', ParentLoginView.as_view(), name='parents_login'),

    # Parent CRUD URLs
    path('kindergarden/parent/', ParentListAPIView.as_view(), name='parent_list'),
    path('kindergarden/parent/add/', ParentCreateAPIView.as_view(), name='parent_add'),
    path('kindergarden/parent/<str:pk>/', ParentRetrieveAPIView.as_view(), name='parent_detail'),
    path('kindergarden/parent/<str:pk>/edit/', ParentUpdateAPIView.as_view(), name='parent_edit'),
    path('kindergarden/parent/<str:pk>/delete/', ParentDeleteAPIView.as_view(), name='parent_delete'),
]

from .views import (
    RoleListAPIView, RoleCreateAPIView, RoleRetrieveAPIView, RoleUpdateAPIView, RoleDeleteAPIView,
    StaffListAPIView, StaffCreateAPIView, StaffRetrieveAPIView, StaffUpdateAPIView, StaffDeleteAPIView
)

urlpatterns += [
    # Roles URLs
    path('kindergarden/roles/', RoleListAPIView.as_view(), name='role_list'),
    path('kindergarden/roles/add/', RoleCreateAPIView.as_view(), name='role_add'),
    path('kindergarden/roles/<str:pk>/', RoleRetrieveAPIView.as_view(), name='role_detail'),
    path('kindergarden/roles/<str:pk>/edit/', RoleUpdateAPIView.as_view(), name='role_edit'),
    path('kindergarden/roles/<str:pk>/delete/', RoleDeleteAPIView.as_view(), name='role_delete'),

    # Staff URLs
    path('kindergarden/staff/', StaffListAPIView.as_view(), name='staff_list'),
    path('kindergarden/staff/add/', StaffCreateAPIView.as_view(), name='staff_add'),
    path('kindergarden/staff/<str:pk>/', StaffRetrieveAPIView.as_view(), name='staff_detail'),
    path('kindergarden/staff/<str:pk>/edit/', StaffUpdateAPIView.as_view(), name='staff_edit'),
    path('kindergarden/staff/<str:pk>/delete/', StaffDeleteAPIView.as_view(), name='staff_delete'),
]
