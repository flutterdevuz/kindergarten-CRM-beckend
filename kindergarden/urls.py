"""
URL configuration for kindergarden project.
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from core.views import landing_page, register_kindergarten, custom_404
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.urls import path, re_path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_page, name='landing'),
    path('register-kindergarten/', register_kindergarten, name='register_kindergarten'),

    # ── API Documentation (ALLOWED_EMAILS orqali himoyalangan) ──
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),

    # ── API Endpoints ──
    path('api/', include('users.urls')),
    path('api/', include('children.urls')),
    path('api/', include('groups.urls')),
    path('api/', include('attendance.urls')),
    path('api/', include('chat.urls')),

    # ── Director Panel + Superadmin Panel ──
    path('', include('core.urls')),
]

# Har qanday holatda media fayllarini serve qilish (ayniqsa DEBUG=False da)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
# Catch-all: har qanday noma'lum URL uchun chiroyli 404 sahifasi
# (DEBUG=True rejimida ham ishlaydi)
urlpatterns += [
    re_path(r'^.*$', custom_404, {'exception': None}),
]

# DEBUG=False uchun ham handler
handler404 = 'core.views.custom_404'
