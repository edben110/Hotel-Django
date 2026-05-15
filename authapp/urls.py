from django.urls import path

from .views import (
    email_sent_view,
    home_view,
    login_view,
    logout_view,
    register_view,
    verify_email_view,
)

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('email-sent/', email_sent_view, name='email_sent'),
    path('verify/', verify_email_view, name='verify_email'),
]
