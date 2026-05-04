from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from backend.serializers import UserSerializer
from django.shortcuts import render, HttpResponse


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]
