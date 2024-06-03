from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from . serializers import RoleSerializer, UserRegistrationSerializer, UserLoginSerializer, UserListSerializer
from . models import Role, User
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
# Create your views here.
def main(request):
    return HttpResponse("This is main")

class RoleList(ListAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class UserRegistrationView(APIView):
    permission_classes = (AllowAny, )
    def post(self,request,format=None):
        serializer = UserRegistrationSerializer(data=request.data) #serializer.data and serializer.error
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            response = {
                    'Message':'Successfully Registered !',
                    'user': serializer.data}
            return Response(response,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = (AllowAny, )
    def post(self,request,format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response = {
                'Message': 'Login Successful',
                #'access': serializer.data['access'],
                #'refresh': serializer.data['refresh'],
                'authenticatedUser': {
                    'email': serializer.data['email'],
                    'role': serializer.data['role']
                }
            }
            return Response(response,status= status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status= status.HTTP_400_BAD_REQUEST)

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
