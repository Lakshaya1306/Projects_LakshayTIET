from django.urls import path
from . import views 
urlpatterns = [
    path("signup/", views.UserSignupView.as_view(), name="user signup"),
    path("login/", views.UserLoginView.as_view(), name = "user login"),
    path('logout/', views.UserLogoutView.as_view(), name="user logout"),
    path('changepassword/', views.UserChangePassword.as_view(), name = "change password"),
    path('forgotpassword/', views.UserForgotPassword.as_view(), name= "forgot password"),
    path('resetpassword/<str:uidb64>/<str:token>/', views.UserResetPassword.as_view(), name = "reset password"),
]
