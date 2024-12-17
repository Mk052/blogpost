from django.shortcuts import render

def home(request):
    return render(request,'authentication/home.html')
# Create your views here.
