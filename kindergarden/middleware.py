"""
Middleware: Maxfiy sahifalarni himoyalash.

/admin/, /api/docs/, /api/schema/ sahifalariga faqat
allowed_emails.py da ro'yxatga olingan emaillar kirishi mumkin.

Agar foydalanuvchi tizimga kirmagan yoki uning emaili ro'yxatda
bo'lmasa — chiroyli 404 sahifasi ko'rsatiladi (mavjudligi yashiriladi).

/panel/ — Director Panel: JWT auth JS tomonida boshqariladi
/superadmin/ — Superadmin Panel: o'z dekoratori bor, middleware to'xtatmaydi
"""

from django.http import Http404
from django.shortcuts import redirect
from kindergarden.allowed_emails import ALLOWED_EMAILS


class RestrictSensitiveURLsMiddleware:
    """
    /admin/, /api/docs/, /api/schema/ ga faqat ALLOWED_EMAILS
    ro'yxatidagi authenticated foydalanuvchilarni kiritadi.
    Boshqalarga 404 qaytaradi (sahifa mavjud emasligini ko'rsatadi).

    /panel/ va /superadmin/ o'z auth sistemalariga ega — bu middleware
    ularni to'xtatmaydi.
    """

    PROTECTED_PREFIXES = (
        '/admin/',
        '/api/docs/',
        '/api/schema/',
    )

    # Bu prefikslar uchun middleware ishlamaydi (o'z auth'lari bor)
    BYPASS_PREFIXES = (
        '/panel/',
        '/superadmin/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # /panel/ va /superadmin/ — o'z auth sistemalari bor, bypass
        if any(path.startswith(prefix) for prefix in self.BYPASS_PREFIXES):
            return self.get_response(request)

        # Login va logout sahifalarini ochiq qoldiramiz (kirish uchun kerak)
        if path.startswith('/admin/login/') or path.startswith('/admin/logout/'):
            return self.get_response(request)

        if any(path.startswith(prefix) for prefix in self.PROTECTED_PREFIXES):
            user = request.user

            # Foydalanuvchi tizimga kirmagan bo'lsa, login sahifasiga yo'naltiramiz
            if not user.is_authenticated:
                return redirect(f'/admin/login/?next={path}')

            # Foydalanuvchi tizimga kirgan, lekin emaili ruxsat ro'yxatida yo'q
            email = getattr(user, 'email', '')
            if email not in ALLOWED_EMAILS:
                raise Http404

        response = self.get_response(request)
        return response

