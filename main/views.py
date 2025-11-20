# views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from .models import Qrcode, User
from .serializers import UserSerializer, UserRegistrationSerializer, QrcodeSerializer, UserFriendSerializer

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'is_staff': user.is_staff
        })

class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserRegistrationSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # UserSerializer ishlatish
        user_serializer = UserSerializer(user)
        
        response_data = {
            'message': 'User muvaffaqiyatli ro\'yxatdan o\'tdi',
            'user': user_serializer.data
        }
        
        # Agar do'st yaratilgan bo'lsa, uning ma'lumotlarini ham qo'shish
        if user.friend:
            friend_serializer = UserSerializer(user.friend)
            response_data['friend'] = friend_serializer.data
            response_data['message'] = 'User va do\'sti muvaffaqiyatli ro\'yxatdan o\'tdi'
        
        return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def user_by_qrcode(request, qr_code):
    try:
        qrcode_obj = Qrcode.objects.get(code=qr_code, is_used=True)
        user = User.objects.get(qr_code=qrcode_obj)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except Qrcode.DoesNotExist:
        return Response(
            {"error": "QR code topilmadi yoki ishlatilmagan"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except User.DoesNotExist:
        return Response(
            {"error": "Ushbu QR code ga bog'langan user topilmadi"}, 
            status=status.HTTP_404_NOT_FOUND
        )

class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class QrcodeListView(generics.ListAPIView):
    queryset = Qrcode.objects.all()
    serializer_class = QrcodeSerializer
    permission_classes = [permissions.IsAdminUser]