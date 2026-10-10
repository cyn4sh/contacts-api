from django.urls import path
from accounts.views import LoginView, LogoutView, RefreshView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", RefreshView.as_view(), name="refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
]