from django.urls import path
from .views import LoginView, CustomSignupView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path("_allauth/browser/v1/auth/signup",
         CustomSignupView.as_view(), name="custom_signup"),

]
