# serializers.py
from rest_framework import serializers
from django.db import transaction
from .models import Qrcode, User

# 1. Avval kichik serializerlar
class QrcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qrcode
        fields = ['id', 'code', 'created_at', 'is_used']
        read_only_fields = ['id', 'created_at', 'is_used']

class FriendRegistrationSerializer(serializers.ModelSerializer):
    """Do'st ro'yxatdan o'tishi uchun to'liq serializer"""
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'middle_name', 'phone_number','gender',
            'telegram_username', 'birth_date', 'email', 'study_place',
            'region', 'district', 'about'
        ]

class UserFriendSerializer(serializers.ModelSerializer):
    """Do'st ma'lumotlari uchun serializer"""
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'phone_number',
            'email', 'telegram_username', 'birth_date', 'study_place','gender',
            'region', 'district', 'about'
        ]

# 2. Keyin asosiy serializerlar
class UserSerializer(serializers.ModelSerializer):
    qr_code_info = serializers.SerializerMethodField()
    friend_info = UserFriendSerializer(source='friend', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'qr_code', 'qr_code_info', 'friend', 'friend_info',
            'first_name', 'last_name', 'middle_name', 'phone_number', 'gender',
            'telegram_username', 'direction', 'birth_date', 'email',
            'study_place', 'region', 'district', 'about', 'is_friend',
            'created_at', 'is_active'
        ]
        read_only_fields = ['id', 'qr_code', 'qr_code_info', 'friend_info', 'created_at', 'is_active']
    
    def get_qr_code_info(self, obj):
        if obj.qr_code:
            return {
                'code': obj.qr_code.code,
                'created_at': obj.qr_code.created_at
            }
        return None

# 3. Oxirgi - registration serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    friend_data = FriendRegistrationSerializer(
        write_only=True, 
        required=False,
        help_text="Do'stning to'liq ma'lumotlari (Robo Futbol uchun majburiy)"
    )
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'middle_name', 'phone_number','gender',
            'telegram_username', 'direction', 'birth_date', 'email',
            'study_place', 'region', 'district', 'about', 'friend_data'
        ]
    
    def validate(self, data):
        direction = data.get('direction')
        friend_data = data.get('friend_data')
        
        # Robo Futbol uchun do'st ma'lumotlari majburiy
        if direction == 'rfutbol':
            if not friend_data:
                raise serializers.ValidationError({
                    'friend_data': "Robo Futbol yo'nalishi uchun do'stning to'liq ma'lumotlari kiritilishi shart"
                })
            
            # Do'st maydonlarini tekshirish
            required_fields = ['first_name', 'last_name', 'phone_number', 'birth_date', 'study_place', 'region', 'district']
            for field in required_fields:
                if not friend_data.get(field):
                    raise serializers.ValidationError({
                        'friend_data': {
                            field: [f'Do\'stning {field} maydoni to\'ldirilishi shart']
                        }
                    })
        
        # Boshqa yo'nalishlar uchun do'st ma'lumotlari bo'lmasligi kerak
        if direction != 'rfutbol' and friend_data:
            raise serializers.ValidationError({
                'friend_data': "Faqat Robo Futbol yo'nalishi uchun do'st ma'lumotlari kiritiladi"
            })
        
        # Do'st emaili asosiy user emaili bilan bir xil bo'lmasligi kerak
        if friend_data and data.get('email') == friend_data.get('email'):
            raise serializers.ValidationError({
                'friend_data': {
                    'email': ['Do\'st emaili sizning emailingiz bilan bir xil bo\'lmasligi kerak']
                }
            })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        friend_data = validated_data.pop('friend_data', None)
        direction = validated_data.get('direction')
        
        # Asosiy user yaratish
        user = User.objects.create(**validated_data)
        
        # Agar Robo Futbol bo'lsa, do'st yaratish
        if direction == 'rfutbol' and friend_data:
            # Do'st uchun email unikal ligini tekshirish
            friend_email = friend_data.get('email')
            if User.objects.filter(email=friend_email).exists():
                raise serializers.ValidationError({
                    'friend_data': {
                        'email': ['Bu email allaqachon ro\'yxatdan o\'tgan']
                    }
                })
            
            # Do'st user yaratish
            friend_user = User.objects.create(
                **friend_data,
                direction='rfutbol',
                is_friend=True
            )
            
            # Asosiy userga do'stni bog'lash
            user.friend = friend_user
            user.save()
            
            # Do'stga ham asosiy userni bog'lash
            friend_user.friend = user
            friend_user.save()
        
        return user