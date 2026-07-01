from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import urllib.request
import urllib.parse
import threading


def landing_page(request):
    """Landing page — bog'cha ro'yxatdan o'tish sahifasi."""
    return render(request, 'landing.html')


def _send_telegram(message: str) -> None:
    """Telegram botga xabar yuborish (fon threadida ishlaydi)."""
    token   = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')
    if not token or not chat_id:
        return
    try:
        url  = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id':    chat_id,
            'text':       message,
            'parse_mode': 'HTML',
        }).encode()
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req, timeout=10):
            pass
    except Exception:
        pass  # Telegram xatosi asosiy jarayonni to'xtatmasin


@require_http_methods(["POST"])
def register_kindergarten(request):
    """
    Bog'cha arizasini qabul qilish.
    POST /register-kindergarten/

    Himoya:
    - Django CSRF middleware (X-CSRFToken header talab qilinadi)
    - Majburiy maydonlar tekshiruvi
    - Ariza qabul qilinganda Telegram botga xabar yuboriladi
    """
    try:
        data = json.loads(request.body)

        name     = data.get('name', '').strip()
        region   = data.get('region', '').strip()
        district = data.get('district', '').strip()
        address  = data.get('address', '').strip()
        phone    = data.get('phone', '').strip()

        # Majburiy maydonlarni tekshirish
        errors = {}
        if not name:
            errors['name'] = "Bog'cha nomini kiriting"
        if not region:
            errors['region'] = "Viloyatni tanlang"
        if not district:
            errors['district'] = "Tumanni tanlang"
        if not phone:
            errors['phone'] = "Telefon raqamini kiriting"
        elif len(phone.replace(' ', '').replace('+', '').replace('-', '')) < 9:
            errors['phone'] = "To'g'ri telefon raqam kiriting"

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        # Ma'lumotlar bazasiga saqlash
        from core.models import KindergartenApplication
        application = KindergartenApplication.objects.create(
            name=name,
            region=region,
            district=district,
            address=address,
            phone=phone,
            status='pending',
        )

        # ── Telegram xabar (fon threadida, asosiy jarayonni sekinlashtirmaydi) ──
        address_line = f"\n📍 <b>Manzil:</b> {address}" if address else ""
        tg_message = (
            "🔔 <b>Yangi ariza keldi!</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"🏫 <b>Bog'cha:</b> {name}\n"
            f"📍 <b>Viloyat:</b> {region}\n"
            f"🏙 <b>Tuman:</b> {district}"
            f"{address_line}\n"
            f"📞 <b>Telefon:</b> {phone}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>Ariza ID:</b> <code>{application.id}</code>\n"
            "⏳ <b>Holat:</b> Kutilmoqda"
        )
        threading.Thread(target=_send_telegram, args=(tg_message,), daemon=True).start()

        return JsonResponse({
            'success': True,
            'message': "Arizangiz qabul qilindi! 24 soat ichida siz bilan bog'lanamiz.",
            'application_id': application.id,
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': "Noto'g'ri so'rov"}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': "Server xatosi. Qaytadan urinib ko'ring."}, status=500)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from children.models import Child
from groups.models import Group
from users.models import StaffProfile, KindergartenRole
from attendance.models import ChildAttendance

class KindergartenStatisticsAPIView(APIView):
    """
    Mobil ilova statistikasi uchun mo'ljallangan Endpoint
    FlChart (LineChart, PieChart, BarChart) formatlariga moslashtirilgan JSON qaytaradi.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        kindergarten = None
        if user.role == 'admin':
            kindergarten = user.admin_profile.kindergarten
        elif user.role == 'staff':
            kindergarten = user.staff_profile.kindergarten
            
        if not kindergarten:
            return Response({"error": "Sizga biriktirilgan bog'cha topilmadi"}, status=403)

        # 1. Summary (Umumiy raqamlar)
        total_children = Child.objects.filter(kindergarten=kindergarten).count()
        total_staff = StaffProfile.objects.filter(kindergarten=kindergarten).count()
        total_groups = Group.objects.filter(kindergarten=kindergarten).count()
        
        today = timezone.now().date()
        today_attendance = ChildAttendance.objects.filter(kindergarten=kindergarten, date=today)
        present_today = today_attendance.filter(status='present').count()
        today_attendance_percent = (present_today / total_children * 100) if total_children > 0 else 0.0

        # 2. Davomat grafigi (So'nggi 7 kun uchun)
        attendance_chart = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            day_records = ChildAttendance.objects.filter(kindergarten=kindergarten, date=d)
            present = day_records.filter(status='present').count()
            absent = day_records.filter(status='absent').count()
            sick = day_records.filter(status='sick').count()
            attendance_chart.append({
                "date": d.strftime("%Y-%m-%d"),
                "present": present,
                "absent": absent,
                "sick": sick
            })

        # 3. Guruhlar grafigi (Qaysi guruhda nechta bola)
        groups = Group.objects.filter(kindergarten=kindergarten).annotate(child_count=Count('children'))
        groups_chart = [{"group_name": g.name, "count": g.child_count} for g in groups]

        # 4. Xodimlar rollari grafigi (PieChart uchun)
        roles = KindergartenRole.objects.filter(kindergarten=kindergarten).annotate(staff_count=Count('staff_profiles'))
        staff_roles_chart = [{"role_name": r.name, "count": r.staff_count} for r in roles]

        return Response({
            "summary": {
                "total_children": total_children,
                "total_staff": total_staff,
                "total_groups": total_groups,
                "today_attendance_percent": round(today_attendance_percent, 1)
            },
            "attendance_chart": attendance_chart,
            "groups_chart": groups_chart,
            "staff_roles_chart": staff_roles_chart
        })


def custom_404(request, exception):
    """Custom 404 sahifasi — chiroyli dizayn bilan."""
    return render(request, '404.html', status=404)


# ══════════════════════════════════════════════════════════════
#  DIRECTOR PANEL — Template views (JWT auth is handled by JS)
# ══════════════════════════════════════════════════════════════

def panel_login(request):
    """Director panel login sahifasi."""
    return render(request, 'panel/login.html')

def panel_dashboard(request):
    """Director panel — dashboard."""
    return render(request, 'panel/dashboard.html')

def panel_groups(request):
    """Director panel — guruhlar."""
    return render(request, 'panel/groups.html')

def panel_staff(request):
    """Director panel — xodimlar."""
    return render(request, 'panel/staff.html')

def panel_children(request):
    """Director panel — bolalar."""
    return render(request, 'panel/children.html')

def panel_parents(request):
    """Director panel — ota-onalar."""
    return render(request, 'panel/parents.html')

def panel_attendance(request):
    """Director panel — davomat."""
    return render(request, 'panel/attendance.html')

def panel_chat(request):
    """Director panel — chat."""
    return render(request, 'panel/chat.html')

def panel_group_detail(request, group_id):
    """Director panel — guruh tafsiloti."""
    return render(request, 'panel/group_detail.html', {'group_id': group_id})


# ══════════════════════════════════════════════════════════════
#  SUPERADMIN PANEL — Session-based auth, server-rendered
# ══════════════════════════════════════════════════════════════

from functools import wraps
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Q
import secrets, string

def superadmin_required(view_func):
    """Decorator: faqat superuser kirishi mumkin."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('/superadmin/login/')
        return view_func(request, *args, **kwargs)
    return wrapper


def superadmin_login(request):
    """Superadmin login — Django session."""
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('/superadmin/')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user and user.is_superuser:
            auth_login(request, user)
            return redirect('/superadmin/')
        else:
            error = "Username yoki parol noto'g'ri, yoki sizda superadmin huquqi yo'q."

    return render(request, 'superadmin/login.html', {'error': error})


def superadmin_logout(request):
    """Superadmin logout."""
    auth_logout(request)
    return redirect('/superadmin/login/')


@superadmin_required
def superadmin_dashboard(request):
    """Superadmin — bosh sahifa, umumiy statistika."""
    from core.models import Kindergarten, KindergartenApplication
    from users.models import KindergartenAdminProfile

    total_kindergartens = Kindergarten.objects.count()
    active_kindergartens = Kindergarten.objects.filter(is_active=True).count()
    total_applications = KindergartenApplication.objects.count()
    pending_applications = KindergartenApplication.objects.filter(status='pending').count()
    recent_applications = KindergartenApplication.objects.order_by('-applied_at')[:8]

    kindergartens_list = []
    for kg in Kindergarten.objects.order_by('-created_at')[:10]:
        admin_count = KindergartenAdminProfile.objects.filter(kindergarten=kg).count()
        kindergartens_list.append({
            'id': kg.id,
            'name': kg.name,
            'is_active': kg.is_active,
            'created_at': kg.created_at,
            'admin_count': admin_count,
        })

    context = {
        'total_kindergartens': total_kindergartens,
        'active_kindergartens': active_kindergartens,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'recent_applications': recent_applications,
        'kindergartens_list': kindergartens_list,
    }
    return render(request, 'superadmin/dashboard.html', context)


@superadmin_required
def superadmin_applications(request):
    """Superadmin — bog'cha arizalari ro'yxati."""
    from core.models import KindergartenApplication
    status_filter = request.GET.get('status', 'all')
    applications = KindergartenApplication.objects.all().order_by('-applied_at')
    if status_filter != 'all':
        applications = applications.filter(status=status_filter)
    context = {
        'applications': applications,
        'status_filter': status_filter,
    }
    return render(request, 'superadmin/applications.html', context)


@superadmin_required
def superadmin_kindergartens(request):
    """Superadmin — barcha bog'chalar ro'yxati."""
    from core.models import Kindergarten
    from users.models import KindergartenAdminProfile
    search = request.GET.get('q', '')
    kindergartens = Kindergarten.objects.all().order_by('-created_at')
    if search:
        kindergartens = kindergartens.filter(name__icontains=search)

    kg_data = []
    for kg in kindergartens:
        admin_count = KindergartenAdminProfile.objects.filter(kindergarten=kg).count()
        kg_data.append({
            'id': kg.id,
            'name': kg.name,
            'is_active': kg.is_active,
            'created_at': kg.created_at,
            'admin_count': admin_count,
        })

    context = {
        'kindergartens': kg_data,
        'search': search,
    }
    return render(request, 'superadmin/kindergartens.html', context)


# ══════════════════════════════════════════════════════════════
#  SUPERADMIN JSON APIs
# ══════════════════════════════════════════════════════════════

from django.views.decorators.http import require_http_methods as _require_http_methods

@superadmin_required
def superadmin_api_applications(request):
    """GET — barcha arizalar JSON."""
    from core.models import KindergartenApplication
    applications = KindergartenApplication.objects.all().order_by('-applied_at')
    data = [
        {
            'id': a.id,
            'name': a.name,
            'region': a.region,
            'district': a.district,
            'address': a.address,
            'phone': a.phone,
            'status': a.status,
            'applied_at': a.applied_at.strftime('%d.%m.%Y %H:%M'),
        }
        for a in applications
    ]
    return JsonResponse({'applications': data})


@superadmin_required
def superadmin_api_update_application(request, app_id):
    """PATCH — ariza holatini o'zgartirish."""
    from core.models import KindergartenApplication
    if request.method != 'PATCH':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        application = KindergartenApplication.objects.get(id=app_id)
        new_status = data.get('status')
        if new_status not in ['pending', 'active', 'inactive']:
            return JsonResponse({'error': "Noto'g'ri holat"}, status=400)
        application.status = new_status
        application.save()
        return JsonResponse({'success': True, 'status': application.status})
    except KindergartenApplication.DoesNotExist:
        return JsonResponse({'error': 'Ariza topilmadi'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@superadmin_required
def superadmin_api_create_kindergarten(request, app_id):
    """
    POST — arizadan bog'cha + admin foydalanuvchi yaratish.
    Body: {username, password}
    """
    from core.models import KindergartenApplication, Kindergarten
    from users.models import User, KindergartenAdminProfile
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        application = KindergartenApplication.objects.get(id=app_id)

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return JsonResponse({'error': "Username va parol kiritilishi shart"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': "Bu username allaqachon mavjud"}, status=400)

        if len(password) < 8:
            return JsonResponse({'error': "Parol kamida 8 ta belgi bo'lishi kerak"}, status=400)

        # 1. Kindergarten yaratish
        kindergarten = Kindergarten.objects.create(
            name=application.name,
            is_active=True,
        )

        # 2. Admin User yaratish
        admin_user = User.objects.create_user(
            username=username,
            password=password,
            role=User.Role.ADMIN,
        )

        # 3. KindergartenAdminProfile bog'lash
        KindergartenAdminProfile.objects.create(
            user=admin_user,
            kindergarten=kindergarten,
        )

        # 4. Arizani 'active' qilish
        application.status = 'active'
        application.save()

        return JsonResponse({
            'success': True,
            'message': f"'{kindergarten.name}' bog'chasi va '{username}' admin muvaffaqiyatli yaratildi!",
            'kindergarten_id': kindergarten.id,
        }, status=201)

    except KindergartenApplication.DoesNotExist:
        return JsonResponse({'error': 'Ariza topilmadi'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@superadmin_required
def superadmin_api_kindergartens(request):
    """GET — barcha bog'chalar JSON."""
    from core.models import Kindergarten
    from users.models import KindergartenAdminProfile
    from children.models import Child
    from users.models import StaffProfile
    kindergartens = Kindergarten.objects.all().order_by('-created_at')
    data = []
    for kg in kindergartens:
        data.append({
            'id': kg.id,
            'name': kg.name,
            'is_active': kg.is_active,
            'created_at': kg.created_at.strftime('%d.%m.%Y'),
            'admin_count': KindergartenAdminProfile.objects.filter(kindergarten=kg).count(),
            'children_count': Child.objects.filter(kindergarten=kg).count(),
            'staff_count': StaffProfile.objects.filter(kindergarten=kg).count(),
        })
    return JsonResponse({'kindergartens': data})


@superadmin_required
def superadmin_api_toggle_kindergarten(request, kg_id):
    """POST — bog'cha faol/nofaol qilish."""
    from core.models import Kindergarten
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        kg = Kindergarten.objects.get(id=kg_id)
        kg.is_active = not kg.is_active
        kg.save()
        return JsonResponse({'success': True, 'is_active': kg.is_active})
    except Kindergarten.DoesNotExist:
        return JsonResponse({'error': "Bog'cha topilmadi"}, status=404)

