from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.decorators import api_view

from home.ansible_job import * 

# Create your views here.
def index(request):
    return HttpResponse("Index Page : Hello, World!")

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def execute_ansible(request):
    print(f'execute_ansible page!')
    ansible_main()
    return HttpResponse("execute_ansible page!")

