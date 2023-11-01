from django.shortcuts import render
from django.http import HttpResponse
from .models import Host

# Create your views here.

def index(request):
    return render(request, "base.html")


def hosts(request):
    return render(request, "hosts.html")