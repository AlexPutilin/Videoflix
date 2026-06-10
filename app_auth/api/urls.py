from django.urls import path
from .views import RegisterView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("activate/<uidb64>/<token>/", name="activate"),
    path("/login/", name="login"),
    path("/logout", name="logout"),
    path("/token/refresh/", name="token_refresh"),
    path("/password_reset/", name="password_reset"),
    path("password_confirm/<uidb64>/<token>/", name="password_confirm"),
]