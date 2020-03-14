from django.urls import path
from . import views

app_name = 'telegram_bot'

urlpatterns = [
    path('callback/<str:bottoken>/', views.callback, name='callback'),
]