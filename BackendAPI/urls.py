from django.urls import path
from .views import main, UserRegistrationView, RoleList, UserLoginView, UserListView

urlpatterns = [
    path('',main),
    path('roles/',RoleList.as_view()),
    path('register/',UserRegistrationView.as_view(),name="register"),
    path('login/',UserLoginView.as_view(),name="login"),
    path('UserList/', UserListView.as_view()),
]