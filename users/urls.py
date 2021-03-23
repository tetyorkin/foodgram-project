from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import SignUp


urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path('password-change/', auth_views.PasswordChangeView.as_view(
            template_name='changePassword.html'), name='password_change'),
    path('login/', auth_views.LoginView.as_view(
        template_name='authForm.html'), name='login'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='resetPassword.html'
         ),
         name='password_reset'),
]
