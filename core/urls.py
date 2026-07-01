from django.urls import path
from .views import (
    KindergartenStatisticsAPIView,
    # Director Panel views
    panel_login, panel_dashboard, panel_groups, panel_staff,
    panel_children, panel_parents, panel_attendance, panel_chat, panel_group_detail,
    # Superadmin views
    superadmin_login, superadmin_logout,
    superadmin_dashboard, superadmin_applications, superadmin_kindergartens,
    # Superadmin JSON APIs
    superadmin_api_applications, superadmin_api_update_application,
    superadmin_api_create_kindergarten, superadmin_api_kindergartens,
    superadmin_api_toggle_kindergarten,
)

app_name = 'core'

urlpatterns = [
    # ── Mobile App Statistics API ──
    path('api/kindergarden/statistic/', KindergartenStatisticsAPIView.as_view(), name='kindergarden_statistic'),

    # ── Director Panel (HTML pages, JWT auth via JS) ──
    path('panel/login/', panel_login, name='panel_login'),
    path('panel/', panel_dashboard, name='panel_dashboard'),
    path('panel/groups/', panel_groups, name='panel_groups'),
    path('panel/groups/<str:group_id>/', panel_group_detail, name='panel_group_detail'),
    path('panel/staff/', panel_staff, name='panel_staff'),
    path('panel/children/', panel_children, name='panel_children'),
    path('panel/parents/', panel_parents, name='panel_parents'),
    path('panel/attendance/', panel_attendance, name='panel_attendance'),
    path('panel/chat/', panel_chat, name='panel_chat'),

    # ── Superadmin Panel (session-based auth) ──
    path('superadmin/login/', superadmin_login, name='superadmin_login'),
    path('superadmin/logout/', superadmin_logout, name='superadmin_logout'),
    path('superadmin/', superadmin_dashboard, name='superadmin_dashboard'),
    path('superadmin/applications/', superadmin_applications, name='superadmin_applications'),
    path('superadmin/kindergartens/', superadmin_kindergartens, name='superadmin_kindergartens'),

    # ── Superadmin JSON APIs ──
    path('superadmin/api/applications/', superadmin_api_applications, name='superadmin_api_applications'),
    path('superadmin/api/applications/<str:app_id>/', superadmin_api_update_application, name='superadmin_api_update_application'),
    path('superadmin/api/applications/<str:app_id>/create-kindergarten/', superadmin_api_create_kindergarten, name='superadmin_api_create_kindergarten'),
    path('superadmin/api/kindergartens/', superadmin_api_kindergartens, name='superadmin_api_kindergartens'),
    path('superadmin/api/kindergartens/<str:kg_id>/toggle/', superadmin_api_toggle_kindergarten, name='superadmin_api_toggle_kindergarten'),
]
