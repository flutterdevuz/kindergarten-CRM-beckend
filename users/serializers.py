from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

User = get_user_model()


class KindergartenLoginSerializer(TokenObtainPairSerializer):
    """Admin/Bog'cha login serializer"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Boshqa rollar kira olmasligi uchun
        if user.role != User.Role.ADMIN:
            raise AuthenticationFailed("Sizda bog'cha admini huquqi yo'q.")
        
        # Admin profilini olish
        try:
            profile = user.admin_profile
            kindergarten = profile.kindergarten
        except Exception:
            raise AuthenticationFailed("Ushbu foydalanuvchiga bog'cha biriktirilmagan.")

        if not kindergarten.is_active:
            raise AuthenticationFailed("Ushbu bog'cha hozirda nofaol (inactive).")

        token['kindergarten_id'] = kindergarten.id
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Payload ma'lumotlarini response body ga ham qo'shamiz
        try:
            kindergarten = self.user.admin_profile.kindergarten
            data['kindergarten_id'] = kindergarten.id
        except Exception:
            pass
        return data


class StaffLoginSerializer(TokenObtainPairSerializer):
    """Xodimlar login serializer"""
    kinder_id = serializers.CharField(required=True, write_only=True)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        kinder_id = attrs.get('kinder_id')
        data = super().validate(attrs)
        
        if self.user.role != User.Role.STAFF:
            raise AuthenticationFailed("Sizda xodim (staff) huquqi yo'q.")

        try:
            profile = self.user.staff_profile
            kindergarten = profile.kindergarten
        except Exception:
            raise AuthenticationFailed("Profil topilmadi.")

        if str(kindergarten.id) != str(kinder_id):
            raise AuthenticationFailed("Siz ushbu bog'cha xodimi emassiz.")

        if not kindergarten.is_active:
            raise AuthenticationFailed("Ushbu bog'cha hozirda nofaol (inactive).")

        # Response payload
        data['kindergarten_id'] = kindergarten.id
        data['staff_id'] = profile.id
        
        # Token ichiga ham qo'shamiz (get_token da qilish uchun extra param uzatish qiyin)
        refresh = self.get_token(self.user)
        refresh['kindergarten_id'] = kindergarten.id
        refresh['staff_id'] = profile.id
        
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        
        # keraksiz kinder_id ni o'chirib tashlaymiz
        data.pop('kinder_id', None)
        return data


class ParentLoginSerializer(TokenObtainPairSerializer):
    """Ota-onalar login serializer"""
    kinder_id = serializers.CharField(required=True, write_only=True)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        kinder_id = attrs.get('kinder_id')
        data = super().validate(attrs)
        
        if self.user.role != User.Role.PARENT:
            raise AuthenticationFailed("Sizda ota-ona (parent) huquqi yo'q.")

        try:
            profile = self.user.parent_profile
            kindergarten = profile.kindergarten
        except Exception:
            raise AuthenticationFailed("Profil topilmadi.")

        if str(kindergarten.id) != str(kinder_id):
            raise AuthenticationFailed("Siz ushbu bog'chada ro'yxatdan o'tmagansiz.")

        if not kindergarten.is_active:
            raise AuthenticationFailed("Ushbu bog'cha hozirda nofaol (inactive).")

        # Response payload
        data['kindergarten_id'] = kindergarten.id
        data['parent_id'] = profile.id
        
        # Token ichiga qo'shamiz
        refresh = self.get_token(self.user)
        refresh['kindergarten_id'] = kindergarten.id
        refresh['parent_id'] = profile.id
        
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        
        data.pop('kinder_id', None)
        return data
