from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import main, UserRegistrationView, RoleList, UserLoginView, UserListView, UserChangePasswordView, ResetPasswordEmailView, UserPasswordResetView

urlpatterns = [
    path('',main),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('roles/',RoleList.as_view()),
    path('register/',UserRegistrationView.as_view(),name="register"),
    path('login/',UserLoginView.as_view(),name="login"),
    path('UserList/', UserListView.as_view()),
    path('ChangePassword/',UserChangePasswordView.as_view(),name="changepassword"),
    path('ResetPasswordEmail/',ResetPasswordEmailView.as_view(),name="resetpassword_email"),
    path('ResetPassword/<userid>/<Reset_Token>/',UserPasswordResetView.as_view(),name="resetpassword"),
]