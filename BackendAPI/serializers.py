from rest_framework import serializers 
from . models import Role, User, UserActivityLog
from .utils import check_for_unusual_activity
from .renderers import UserErrorRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id','roles']

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'role']
        extra_kwargs = {'password': {'write_only': True}}
        def validate_email(self, value):
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("This email is already registered.")
            return value

class UserLoginSerializer(serializers.Serializer):
    renderer_classes = [UserErrorRenderer]
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)

    def create(self, validated_date):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        email = data['email']
        password = data['password']
        user = authenticate(email=email, password=password)

        if user is None:
            # Log failed login attempt
            UserActivityLog.objects.create(user=User.objects.filter(email=email).first(), activity_type='login', details='Failed login attempt')
            # Check for unusual activity
            check_for_unusual_activity(User.objects.filter(email=email).first())
            raise serializers.ValidationError("Invalid login credentials")

        try:
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh)
            access_token = str(refresh.access_token)

            update_last_login(None, user)

            validation = {
                'access': access_token,
                'refresh': refresh_token,
                'email': user.email,
                'role': user.role,
            }

            return validation
        except user.DoesNotExist:
            raise serializers.ValidationError("Invalid login credentials")
        
class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128,style={'input_type':'password'},write_only=True)
    ConfirmPassword = serializers.CharField(max_length=128,style={'input_type':'password'},write_only=True)
    class Meta:
        fields = ['password','ConfirmPassword']
    def validate(self, attrs):
        password = attrs.get('password')        
        ConfirmPassword = attrs.get('ConfirmPassword')
        user = self.context.get('user')
        if password != ConfirmPassword :
            raise serializers.ValidationError("Password And Confirm Password does not match")
        user.set_password(password)
        user.save()
        return attrs  
    
def send_resetpassword_email(email,Reset_link):
        subject = 'Reset Password'
        message = f'Password Reset Link Details \n\nEmail: {email}\nReset Link : {Reset_link}'
        send_mail(subject, message, 'aura.riskdashboard@gmail.com', [email])

class PasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        fields = ['email']
    def validate(self, attrs):
        email = attrs.get('email')
        if  User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            userid = urlsafe_base64_encode(force_bytes(user.id))
            Reset_Token = PasswordResetTokenGenerator().make_token(user)
            Reset_link = 'http://localhost:3000/api/Reset/'+userid+'/'+Reset_Token
            print("Reset Link: ",Reset_link)
            send_resetpassword_email(email,Reset_link)
            return attrs
        else:
            raise serializers.ValidationError("Email does not exists !")
        
class UserPasswordResetSerializer(serializers.Serializer):
    Resetpassword = serializers.CharField(max_length=128,style={'input_type':'password'},write_only=True)
    ConfirmPassword = serializers.CharField(max_length=128,style={'input_type':'password'},write_only=True)
    class Meta:
        fields = ['Resetpassword','ConfirmPassword']
    def validate(self, attrs):
        Resetpassword = attrs.get('Resetpassword')        
        ConfirmPassword = attrs.get('ConfirmPassword')
        userid = self.context.get('userid')
        Reset_Token = self.context.get('Reset_Token')
        if Resetpassword != ConfirmPassword :
            raise serializers.ValidationError("Reset Password And Confirm Password does not match")
        userid = smart_str(urlsafe_base64_decode(userid))
        user = User.objects.get(id=userid)
        if not PasswordResetTokenGenerator().check_token(user,Reset_Token):
            raise ValidationError('Invalid Token or Expired')
        user.set_password(Resetpassword)
        user.save()
        return attrs
    
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'role'
        )