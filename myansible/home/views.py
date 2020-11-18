from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.decorators import api_view

# Create your views here.
def index(request):
    return HttpResponse("Index Page : Hello, World!")

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def execute_ansible(request):
    print(f'Start execute_ansible page!')
    return HttpResponse("execute_ansible page!")

