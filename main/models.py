from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
import random


class Qrcode(models.Model): 
    code = models.CharField(
        max_length=12, 
        unique=True,
        validators=[MinLengthValidator(8)]
    )
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return self.code
    
    @classmethod
    def generate_code(cls):
        while True:
            code = ''.join(random.choices('0123456789', k=8))
            if not cls.objects.filter(code=code).exists():
                return code



class User(models.Model):
    DIRECTION_CHOICES = [
        ('rfutbol', 'Robo Futbol'),
        ('rsumo', 'Robo sumo'),
        ('fixtirolar', 'Foydali Ixtirolar'),
        ('ai', 'Ai'),
        ('contest', 'Contest'),
        
    ]
    
    qr_code = models.OneToOneField( 
        Qrcode, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        unique=True
    )
    friend = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='friends',
        verbose_name="Do'st (Robo Futbol uchun)"
    )
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=20, blank=True)  
    phone_number = models.CharField(max_length=20)
    telegram_username = models.CharField(max_length=50, null=True, blank=True)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)
    birth_date = models.DateField(default="")
    gender = models.CharField(max_length=20)
    email = models.EmailField(null=True,blank=True)
    study_place = models.CharField(max_length=100)
    region = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    about = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_friend = models.BooleanField(default=False, verbose_name="Do'st bilan ishtirok etadi")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    # def clean(self):
    #     """Modelni tozalash - validatsiya qilish"""
    #     from django.core.exceptions import ValidationError
        
    #     # Robo Futbol uchun do'st majburiy
    #     if self.direction == 'rfutbol' and not self.friend:
    #         raise ValidationError({
    #             'friend': "Robo Futbol yo'nalishi uchun do'st tanlashingiz kerak"
    #         })
        
    #     # Do'st o'zi ham Robo Futbol tanlash kerak
    #     if self.friend and self.friend.direction != 'rfutbol':
    #         raise ValidationError({
    #             'friend': "Do'st ham Robo Futbol yo'nalishini tanlashi kerak"
    #         })
        
    #     # O'zini o'ziga do'st qilib belgilashni oldini olish
    #     if self.friend and self.friend.id == self.id:
    #         raise ValidationError({
    #             'friend': "O'zingizni o'zingizga do'st qilib belgilay olmaysiz"
    #         })
    
    def save(self, *args, **kwargs):
        # Avtomatik QR code yaratish
        if not self.pk and not self.qr_code:
            qr_code = Qrcode.objects.create(
                code=Qrcode.generate_code(),
                is_used=True
            )
            self.qr_code = qr_code
        
        # Robo Futbol yo'nalishi uchun is_friend ni avtomatik sozlash
        # if self.direction == 'rfutbol':
        #     self.is_friend = True
        # else:
        #     self.is_friend = False
        #     self.friend = None
        
        # Validatsiyani tekshirish (faqat friend mavjud bo'lsa)
        # if self.friend:
        #     self.full_clean()
        
        super().save(*args, **kwargs)
    
    # @property
    # def has_friend(self):
    #     return self.friend is not None
    
    # @property
    # def friend_info(self):
    #     if self.friend:
    #         return {
    #             'id': self.friend.id,
    #             'full_name': f"{self.friend.first_name} {self.friend.last_name}",
    #             'phone': self.friend.phone_number,
    #             'email': self.friend.email,
    #             'study_place': self.friend.study_place,
    #             'birth_date': self.friend.birth_date
    #         }
    #     return None
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"