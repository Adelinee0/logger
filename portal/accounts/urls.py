from .views import SignUp, upgrade_user
from django.urls import path, include

urlpatterns = [
    #path('signup', SignUp.as_view(), name='signup'),
    path('', include('allauth.urls')),
    path('upgrade/', upgrade_user, name='account_upgrade'),
]