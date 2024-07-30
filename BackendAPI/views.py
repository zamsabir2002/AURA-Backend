from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from . serializers import RoleSerializer, UserRegistrationSerializer, UserLoginSerializer, UserListSerializer, UserChangePasswordSerializer, PasswordResetEmailSerializer, UserPasswordResetSerializer
from . models import Role, User, UserActivityLog
from .utils import check_for_unusual_activity
from django.contrib.auth import authenticate, get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail

# Create your views here.
def main(request):
    return HttpResponse("This is main")

class RoleList(ListAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
def get_user_token(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh' : str(refresh),
        'access' : str(refresh.access_token),
    }
class UserRegistrationView(APIView):
    #authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    def post(self, request):
        if not request.user.is_admin: 
            return Response({'message': 'Only Admin can register users'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Generate random password
            password = User.objects.make_random_password()
            user = User.objects.create_user(
                email=serializer.validated_data['email'],
                name=serializer.validated_data['name'],
                password=password,
                role=serializer.validated_data['role'],
            )
            token = get_user_token(user)
            # Send registration email
            send_registration_email(user.email, user.name, password)
            return Response({'message': 'User registered successfully', 'Token' : token})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def send_registration_email(email, name, password):
        subject = 'Registration Details'
        message = f'Hello {name},\n\nYour registration is successful.\n\nEmail: {email}\nPassword: {password}'
        send_mail(subject, message, 'aura.riskdashboard@gmail.com', [email])

User = get_user_model()
class UserLoginView(APIView):
    permission_classes = (AllowAny, )
    def post(self,request,format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response = {
                'Message': 'Login Successful',
                'authenticatedUser': {
                    'email': serializer.data['email'],
                    'role': serializer.data['role'],
                    'refresh': serializer.data['refresh'],
                    'access': serializer.data['access']
                }
            }
            return Response(response,status= status.HTTP_200_OK)
        else:
            email = request.data.get('email')
            if email:
                print("email exists")
                user = User.objects.filter(email=email).first()
                if user:
                    print(f"Creating activity log for user: {user.email}")
                    UserActivityLog.objects.create(user=user, activity_type='login', details='Failed login attempt')
                    check_for_unusual_activity(user)  # Checking for anomalies
            return Response(serializer.errors,status= status.HTTP_400_BAD_REQUEST)
def send_password_change_notification(user):
    subject = 'Password Changed Successfully'
    message = f'Hello {user.name},\n\nYour password has been changed successfully\n\nBest Regards,\nTeam AURA'
    send_mail(subject, message, 'aura.riskdashboard@gmail.com', [user.email])

class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request,format=None):
        serializer = UserChangePasswordSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            send_password_change_notification(request.user)
            return Response({'Message':'Password Changed Successfully!'},status=status.HTTP_200_OK)

class ResetPasswordEmailView(APIView):
    permission_classes = (AllowAny, )
    def post(self,request,format=None):
        serializer = PasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'Message':'Password resent link sent ! '},status= status.HTTP_200_OK)
        
class UserPasswordResetView(APIView):
    permission_classes = (AllowAny,)
    def post(self,request,userid,Reset_Token,format=None):
        serializer = UserPasswordResetSerializer(data=request.data,context={'userid':userid,'Reset_Token':Reset_Token})
        if serializer.is_valid(raise_exception=True):
            return Response({'Message':'Password has been reset successfully !'},status=status.HTTP_200_OK)
        
class UserListView(APIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        if user.role != 1:
            response = {
                'success': False,
                'status_code': status.HTTP_403_FORBIDDEN,
                'Message': 'You are not authorized to perform this action'
            }
            return Response(response, status.HTTP_403_FORBIDDEN)
        else:
            users = User.objects.all()
            serializer = self.serializer_class(users, many=True)
            response = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'Message': 'Successfully Fetched Users',
                'Users': serializer.data

            }
            return Response(response, status=status.HTTP_200_OK)
