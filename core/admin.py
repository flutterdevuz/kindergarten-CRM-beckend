from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import localtime
from core.models import KindergartenApplication


@admin.register(KindergartenApplication)
class KindergartenApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'region', 'district', 'phone',
        'status_badge', 'applied_at_formatted',
    )
    list_filter = ('status', 'region')
    search_fields = ('name', 'phone', 'district', 'region')
    readonly_fields = ('id', 'applied_at', 'updated_at')
    list_per_page = 25
    ordering = ('-applied_at',)

    fieldsets = (
        ("Bog'cha ma'lumotlari", {
            'fields': ('id', 'name', 'region', 'district', 'address', 'phone')
        }),
        ("Holat va vaqt", {
            'fields': ('status', 'applied_at', 'updated_at')
        }),
    )

    actions = ['make_active', 'make_inactive', 'make_pending']

    def status_badge(self, obj):
        colors = {
            'pending':  ('#f59e0b', '#1a1200', '⏳ Kutilmoqda'),
            'active':   ('#22c55e', '#001a08', '✅ Faol'),
            'inactive': ('#ef4444', '#1a0000', '❌ Nofaol'),
        }
        color, bg, label = colors.get(obj.status, ('#999', '#111', obj.status))
        return format_html(
            '<span style="'
            'background:{bg};color:{color};'
            'padding:4px 12px;border-radius:100px;'
            'font-size:0.78rem;font-weight:600;'
            'border:1px solid {color}33;'
            'white-space:nowrap'
            '">{label}</span>',
            bg=bg, color=color, label=label
        )
    status_badge.short_description = 'Holat'

    def applied_at_formatted(self, obj):
        return localtime(obj.applied_at).strftime('%d.%m.%Y %H:%M')
    applied_at_formatted.short_description = 'Ariza vaqti'

    @admin.action(description='✅ Faol qilish')
    def make_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f"{updated} ta ariza Faol holatiga o'zgartirildi.")

    @admin.action(description='❌ Nofaol qilish')
    def make_inactive(self, request, queryset):
        updated = queryset.update(status='inactive')
        self.message_user(request, f"{updated} ta ariza Nofaol holatiga o'zgartirildi.")

    @admin.action(description='⏳ Kutilmoqda holatiga qaytarish')
    def make_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f"{updated} ta ariza Kutilmoqda holatiga qaytarildi.")
