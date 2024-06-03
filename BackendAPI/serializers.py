from rest_framework import serializers 
from . models import Role, User
from .renderers import UserErrorRenderer
#from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id','username','roles']

class UserRegistrationSerializer(serializers.ModelSerializer):
    renderer_classes = [UserErrorRenderer]
    pass2 = serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model = User
        fields = ['email','name','password','pass2','role']
        extra_kwargs={
            'password':{'write_only':True}
        }
    def validate(self,attrs):
        password = attrs.get('password')
        password2 = attrs.get('pass2')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password dosent match !")
        return attrs
    def create(self,validate_date):
        auth_user = User.objects.create_user(**validate_date)
        return auth_user

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
            raise serializers.ValidationError("Invalid login credentials")

        try:
            #refresh = RefreshToken.for_user(user)
            #refresh_token = str(refresh)
            #access_token = str(refresh.access_token)

            update_last_login(None, user)

            validation = {
                #'access': access_token,
                #'refresh': refresh_token,
                'email': user.email,
                'role': user.role,
            }

            return validation
        except user.DoesNotExist:
            raise serializers.ValidationError("Invalid login credentials")
 
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'role'
        )