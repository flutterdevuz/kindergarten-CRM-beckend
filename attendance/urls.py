from django.urls import path
from .views import (
    AttendanceListAPIView, BulkAttendanceMarkAPIView, 
    AttendanceUpdateAPIView, AttendanceDeleteAPIView
)

app_name = 'attendance'

urlpatterns = [
    path('kindergarden/attendance/', AttendanceListAPIView.as_view(), name='attendance_list'),
    path('kindergarden/attendance/mark/', BulkAttendanceMarkAPIView.as_view(), name='attendance_mark_bulk'),
    path('kindergarden/attendance/<str:pk>/edit/', AttendanceUpdateAPIView.as_view(), name='attendance_edit'),
    path('kindergarden/attendance/<str:pk>/delete/', AttendanceDeleteAPIView.as_view(), name='attendance_delete'),
]
