from django.urls import path
from authentication import views

urlpatterns = [
    path('home/',views.home,name="home"),
]